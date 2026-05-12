import json
import os
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class Note:
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)

@dataclass
class Task:
    title: str
    completed: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    due_date: Optional[str] = None

class StorageManager:
    def __init__(self, file_path: str = "data.json"):
        self.file_path = file_path
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"notes": [], "tasks": []}

    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.data, f, indent=4)

    def add_note(self, note: Note):
        self.data["notes"].append(asdict(note))
        self.save()

    def add_task(self, task: Task):
        self.data["tasks"].append(asdict(task))
        self.save()

    def get_notes(self) -> List[Dict[str, Any]]:
        return self.data.get("notes", [])

    def get_tasks(self) -> List[Dict[str, Any]]:
        return self.data.get("tasks", [])
