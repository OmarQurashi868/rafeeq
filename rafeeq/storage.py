import json
import os
import re
import secrets
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from rafeeq.notifications import WindowsNotificationManager

def generate_id() -> str:
    return secrets.token_hex(3)

@dataclass
class Note:
    content: str
    id: str = field(default_factory=generate_id)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)

@dataclass
class Task:
    title: str
    id: str = field(default_factory=generate_id)
    completed: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    due_date: Optional[str] = None

class StorageManager:
    def __init__(self, file_path: str = "data.json"):
        self.file_path = file_path
        self.data = self._load_data()
        self._migrate_ids()
        self.notifier = WindowsNotificationManager()

    def _load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"notes": [], "tasks": []}

    def _migrate_ids(self):
        updated = False
        from datetime import timedelta
        # Use a fixed baseline to ensure sequential timestamps for legacy items
        baseline = datetime.now()
        
        notes = self.data.get("notes", [])
        for i, note in enumerate(notes):
            if "id" not in note:
                note["id"] = generate_id()
                updated = True
            if "timestamp" not in note:
                # Legacy items are assigned timestamps in the order they appear, 
                # but slightly separated to ensure stable sorting.
                ts = (baseline - timedelta(days=365) + timedelta(seconds=i)).isoformat()
                note["timestamp"] = ts
                updated = True
        
        tasks = self.data.get("tasks", [])
        for i, task in enumerate(tasks):
            if "id" not in task:
                task["id"] = generate_id()
                updated = True
            if "timestamp" not in task:
                ts = (baseline - timedelta(days=365) + timedelta(seconds=i)).isoformat()
                task["timestamp"] = ts
                updated = True
        if updated:
            self.save()

    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.data, f, indent=4)

    def add_note(self, note: Note) -> Note:
        self.data["notes"].append(asdict(note))
        self.save()
        return note

    def delete_note(self, note_id: str) -> bool:
        initial_len = len(self.data["notes"])
        self.data["notes"] = [n for n in self.data["notes"] if n["id"] != note_id]
        if len(self.data["notes"]) < initial_len:
            self.save()
            return True
        return False

    def update_note(self, note_id: str, content: str) -> bool:
        for note in self.data["notes"]:
            if note["id"] == note_id:
                note["content"] = content
                self.save()
                return True
        return False

    def add_task(self, task: Task) -> Task:
        self.data["tasks"].append(asdict(task))
        self.save()
        if task.due_date and not task.completed:
            self.notifier.schedule_reminder(task.id, task.title, task.due_date)
        return task

    def delete_task(self, task_id: str) -> bool:
        initial_len = len(self.data["tasks"])
        self.data["tasks"] = [t for t in self.data["tasks"] if t["id"] != task_id]
        if len(self.data["tasks"]) < initial_len:
            self.save()
            self.notifier.remove_reminder(task_id)
            return True
        return False

    def update_task(self, task_id: str, title: Optional[str] = None, due_date: Optional[str] = None, completed: Optional[bool] = None) -> bool:
        for task in self.data["tasks"]:
            if task["id"] == task_id:
                if title is not None:
                    task["title"] = title
                if due_date is not None:
                    task["due_date"] = due_date
                if completed is not None:
                    task["completed"] = completed
                self.save()
                
                # Sync notification
                if task["completed"] or not task["due_date"]:
                    self.notifier.remove_reminder(task_id)
                elif task["due_date"]:
                    self.notifier.schedule_reminder(task_id, task["title"], task["due_date"])
                
                return True
        return False

    def get_indexed_items(self, category: str, include_completed: bool = True) -> List[Dict[str, Any]]:
        """Returns items in category sorted by timestamp with a 1-based index. 
        Optionally filters out completed tasks for compact numbering."""
        items = self.data.get(category, [])
        if category == "tasks" and not include_completed:
            items = [t for t in items if not t.get("completed", False)]
            
        # Sort by timestamp (oldest first)
        sorted_items = sorted(items, key=lambda x: x.get("timestamp", ""))
        results = []
        for i, item in enumerate(sorted_items, 1):
            item_copy = item.copy()
            item_copy["index"] = i
            results.append(item_copy)
        return results

    def resolve_indices(self, category: str, selector: str) -> List[str]:
        """
        Parses numeric selector (e.g. '1', '1-3', '1,2,5') into internal hex IDs.
        For tasks, defaults to PENDING items for compact numbering consistency.
        Returns a list of matching hex IDs.
        """
        # If it's tasks, we try to resolve against pending tasks first as that's 
        # what the user usually sees in the sidebar/brief.
        include_completed = False
        if "all" in selector.lower():
             include_completed = True
             selector = selector.lower().replace("all", "").strip()

        indexed_items = self.get_indexed_items(category, include_completed=include_completed)
        resolved_ids = []
        
        # Pre-process common natural language range words
        clean_selector = selector.lower().replace(" through ", "-").replace(" to ", "-")
        parts = [p.strip() for p in clean_selector.split(",")]
        
        for part in parts:
            if not part: continue
            if "-" in part:
                try:
                    start_str, end_str = part.split("-", 1)
                    start_num_str = re.sub(r"\D", "", start_str)
                    end_num_str = re.sub(r"\D", "", end_str)
                    if not start_num_str or not end_num_str:
                        continue
                    start = int(start_num_str)
                    end = int(end_num_str)
                    for i in range(min(start, end), max(start, end) + 1):
                        if 1 <= i <= len(indexed_items):
                            resolved_ids.append(indexed_items[i-1]["id"])
                except (ValueError, IndexError):
                    continue
            else:
                try:
                    numeric_match = re.search(r"(\d+)", part)
                    if numeric_match:
                        idx = int(numeric_match.group(1))
                        if 1 <= idx <= len(indexed_items):
                            resolved_ids.append(indexed_items[idx-1]["id"])
                        else:
                            # Fallback: maybe they meant the index in the FULL list?
                            if not include_completed and category == "tasks":
                                full_items = self.get_indexed_items(category, include_completed=True)
                                if 1 <= idx <= len(full_items):
                                    resolved_ids.append(full_items[idx-1]["id"])
                    else:
                        # Fallback: check if it's a hex ID or title match
                        for item in self.data.get(category, []):
                            if item["id"] == part or (category == "tasks" and item["title"].lower() == part.lower()):
                                resolved_ids.append(item["id"])
                except ValueError:
                    continue
        
        return list(dict.fromkeys(resolved_ids))

    def get_notes(self) -> List[Dict[str, Any]]:
        return self.data.get("notes", [])

    def get_tasks(self) -> List[Dict[str, Any]]:
        return self.data.get("tasks", [])

    def complete_task(self, identifier: str) -> bool:
        updated = False
        for task in self.data.get("tasks", []):
            # Support both ID and title for backward compatibility/flexibility
            if task["id"] == identifier or task["title"].lower() == identifier.lower():
                task["completed"] = True
                self.notifier.remove_reminder(task["id"])
                updated = True
        if updated:
            self.save()
        return updated

    def search(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        query = query.lower()
        results = {"notes": [], "tasks": []}
        
        for note in self.data.get("notes", []):
            if query in note["content"].lower():
                results["notes"].append(note)
        
        for task in self.data.get("tasks", []):
            if query in task["title"].lower():
                results["tasks"].append(task)
        
        return results

    def get_daily_summary(self) -> Dict[str, Any]:
        from datetime import date
        today = date.today().isoformat()
        
        pending_tasks = [t for t in self.data.get("tasks", []) if not t["completed"]]
        recent_notes = self.data.get("notes", [])[-5:] # Last 5 notes
        
        return {
            "pending_tasks_count": len(pending_tasks),
            "pending_tasks": pending_tasks,
            "recent_notes": recent_notes
        }
