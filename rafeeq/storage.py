import json
import os
import secrets
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Dict, Any, Optional

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
        for note in self.data.get("notes", []):
            if "id" not in note:
                note["id"] = generate_id()
                updated = True
        for task in self.data.get("tasks", []):
            if "id" not in task:
                task["id"] = generate_id()
                updated = True
        if updated:
            self.save()

    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.data, f, indent=4)

    def add_note(self, note: Note):
        self.data["notes"].append(asdict(note))
        self.save()

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

    def add_task(self, task: Task):
        self.data["tasks"].append(asdict(task))
        self.save()

    def delete_task(self, task_id: str) -> bool:
        initial_len = len(self.data["tasks"])
        self.data["tasks"] = [t for t in self.data["tasks"] if t["id"] != task_id]
        if len(self.data["tasks"]) < initial_len:
            self.save()
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
                return True
        return False

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
