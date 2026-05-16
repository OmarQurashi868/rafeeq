import os
import pytest
from rafeeq.storage import StorageManager, Task, Note
from rafeeq.logic import execute_intents

TEST_DB = "test_intents.json"

@pytest.fixture
def storage():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    sm = StorageManager(file_path=TEST_DB)
    yield sm
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_save_note_intent(storage):
    text = "Sure, I'll save that. [SAVE_NOTE: This is a test note]"
    clean, obs = execute_intents(text, storage)
    assert "Sure, I'll save that." in clean
    assert any("Note saved with ID" in o for o in obs)
    assert len(storage.get_notes()) == 1

def test_add_task_intent(storage):
    text = "Adding it to your list. [ADD_TASK: Buy milk | DUE: 2026-05-16 10:00]"
    clean, obs = execute_intents(text, storage)
    assert "Adding it to your list." in clean
    assert any("Task added with ID" in o and "Buy milk" in o for o in obs)
    assert len(storage.get_tasks()) == 1

def test_update_note_intent(storage):
    n = storage.add_note(Note(content="Old note"))
    note_id = n.id
    text = f"Updating it. [UPDATE_NOTE: {note_id} | New content]"
    clean, obs = execute_intents(text, storage)
    assert "Updating it." in clean
    assert any(f"Note [{note_id}] updated successfully" in o for o in obs)
    assert storage.get_notes()[0]["content"] == "New content"

def test_delete_note_intent(storage):
    n = storage.add_note(Note(content="Bye bye"))
    note_id = n.id
    text = f"Deleting. [DELETE_NOTE: {note_id}]"
    clean, obs = execute_intents(text, storage)
    assert "Deleting." in clean
    assert any(f"Note [{note_id}] deleted" in o for o in obs)
    assert len(storage.get_notes()) == 0

def test_update_task_intent(storage):
    t = storage.add_task(Task(title="Old task"))
    task_id = t.id
    text = f"Updating task. [UPDATE_TASK: {task_id} | TITLE: New Title | COMPLETED: true]"
    clean, obs = execute_intents(text, storage)
    assert "Updating task." in clean
    assert any(f"Task [{task_id}] updated successfully" in o for o in obs)
    task = storage.get_tasks()[0]
    assert task["title"] == "New Title"
    assert task["completed"] is True

def test_delete_task_intent(storage):
    t = storage.add_task(Task(title="Remove me"))
    task_id = t.id
    text = f"Removing. [DELETE_TASK: {task_id}]"
    clean, obs = execute_intents(text, storage)
    assert "Removing." in clean
    assert any(f"Task [{task_id}] deleted" in o for o in obs)
    assert len(storage.get_tasks()) == 0

def test_list_notes_with_ids(storage):
    n = storage.add_note(Note(content="Note with ID"))
    note_id = n.id
    text = "Show notes. [LIST_NOTES]"
    clean, obs = execute_intents(text, storage)
    assert any(f"[{note_id}]" in o for o in obs)
    assert any("Note with ID" in o for o in obs)

def test_list_tasks_with_ids(storage):
    t = storage.add_task(Task(title="Task with ID"))
    task_id = t.id
    text = "Show tasks. [LIST_TASKS]"
    clean, obs = execute_intents(text, storage)
    assert any(f"[{task_id}]" in o for o in obs)
    assert any("Task with ID" in o for o in obs)

def test_complete_task_intent(storage):
    storage.add_task(Task(title="Finish homework"))
    text = "Done! [COMPLETE_TASK: Finish homework]"
    clean, obs = execute_intents(text, storage)
    assert any("Task [Finish homework] marked as completed" in o for o in obs)
    assert storage.get_tasks()[0]["completed"] is True

def test_search_intent(storage):
    storage.add_note(Note(content="Apple pie recipe"))
    text = "I'll look for that. [SEARCH: apple]"
    clean, obs = execute_intents(text, storage)
    assert any("Search results for 'apple'" in o for o in obs)
    assert any("Apple pie recipe" in o for o in obs)

def test_daily_brief_intent(storage):
    storage.add_task(Task(title="Buy eggs"))
    text = "Here is your update. [DAILY_BRIEF]"
    clean, obs = execute_intents(text, storage)
    assert any("Daily Briefing" in o for o in obs)
    assert any("Pending tasks: 1" in o for o in obs)
    assert any("Buy eggs" in o for o in obs)
