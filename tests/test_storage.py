import os
import pytest
from rafeeq.storage import StorageManager, Note, Task

TEST_DB = "test_data.json"

@pytest.fixture
def storage():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    sm = StorageManager(file_path=TEST_DB)
    yield sm
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_add_note(storage):
    note = Note(content="Test note")
    storage.add_note(note)
    notes = storage.get_notes()
    assert len(notes) == 1
    assert notes[0]["content"] == "Test note"
    assert len(notes[0]["id"]) == 6

def test_add_task(storage):
    task = Task(title="Test task")
    storage.add_task(task)
    tasks = storage.get_tasks()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Test task"
    assert tasks[0]["completed"] is False
    assert len(tasks[0]["id"]) == 6

def test_delete_note(storage):
    note = Note(content="Delete me")
    storage.add_note(note)
    note_id = storage.get_notes()[0]["id"]
    assert storage.delete_note(note_id) is True
    assert len(storage.get_notes()) == 0

def test_update_note(storage):
    note = Note(content="Update me")
    storage.add_note(note)
    note_id = storage.get_notes()[0]["id"]
    assert storage.update_note(note_id, "Updated content") is True
    assert storage.get_notes()[0]["content"] == "Updated content"

def test_delete_task(storage):
    task = Task(title="Delete task")
    storage.add_task(task)
    task_id = storage.get_tasks()[0]["id"]
    assert storage.delete_task(task_id) is True
    assert len(storage.get_tasks()) == 0

def test_update_task(storage):
    task = Task(title="Update task")
    storage.add_task(task)
    task_id = storage.get_tasks()[0]["id"]
    assert storage.update_task(task_id, title="New Title", completed=True) is True
    updated_task = storage.get_tasks()[0]
    assert updated_task["title"] == "New Title"
    assert updated_task["completed"] is True

def test_complete_task_by_id(storage):
    task = Task(title="Complete by ID")
    storage.add_task(task)
    task_id = storage.get_tasks()[0]["id"]
    success = storage.complete_task(task_id)
    assert success is True
    assert storage.get_tasks()[0]["completed"] is True

def test_migration(storage):
    # Manually inject data without IDs
    storage.data = {
        "notes": [{"content": "Old note", "timestamp": "2024-01-01"}],
        "tasks": [{"title": "Old task", "completed": False, "timestamp": "2024-01-01"}]
    }
    storage.save()
    
    # Reload storage to trigger migration
    new_storage = StorageManager(file_path=TEST_DB)
    assert "id" in new_storage.get_notes()[0]
    assert "id" in new_storage.get_tasks()[0]
    assert len(new_storage.get_notes()[0]["id"]) == 6

def test_persistence(storage):
    storage.add_note(Note(content="Persistent note"))
    # Create a new storage instance pointing to same file
    new_storage = StorageManager(file_path=TEST_DB)
    assert len(new_storage.get_notes()) == 1
    assert new_storage.get_notes()[0]["content"] == "Persistent note"

def test_search(storage):
    storage.add_note(Note(content="Find this note"))
    storage.add_task(Task(title="Find this task"))
    results = storage.search("Find")
    assert len(results["notes"]) == 1
    assert len(results["tasks"]) == 1
    assert results["notes"][0]["content"] == "Find this note"

def test_daily_summary(storage):
    storage.add_note(Note(content="Recent note"))
    storage.add_task(Task(title="Pending task", completed=False))
    storage.add_task(Task(title="Done task", completed=True))
    summary = storage.get_daily_summary()
    assert summary["pending_tasks_count"] == 1
    assert len(summary["recent_notes"]) == 1
