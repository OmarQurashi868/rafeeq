import os
import pytest
from rafeeq.storage import StorageManager, Task, Note
from rafeeq.logic import process_ai_intent

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
    response = process_ai_intent(text, storage)
    assert "✅ **Note saved:** This is a test note" in response
    assert "[SAVE_NOTE:" not in response
    assert len(storage.get_notes()) == 1

def test_add_task_intent(storage):
    text = "Adding it to your list. [ADD_TASK: Buy milk | DUE: 2026-05-16 10:00]"
    response = process_ai_intent(text, storage)
    assert "✅ **Task added:** Buy milk (Due: 2026-05-16 10:00)" in response
    assert "[ADD_TASK:" not in response
    assert len(storage.get_tasks()) == 1

def test_update_note_intent(storage):
    storage.add_note(Note(content="Old note"))
    note_id = storage.get_notes()[0]["id"]
    text = f"Updating it. [UPDATE_NOTE: {note_id} | New content]"
    response = process_ai_intent(text, storage)
    assert f"✅ **Note updated:** [{note_id}] New content" in response
    assert storage.get_notes()[0]["content"] == "New content"

def test_delete_note_intent(storage):
    storage.add_note(Note(content="Bye bye"))
    note_id = storage.get_notes()[0]["id"]
    text = f"Deleting. [DELETE_NOTE: {note_id}]"
    response = process_ai_intent(text, storage)
    assert f"✅ **Note deleted:** {note_id}" in response
    assert len(storage.get_notes()) == 0

def test_update_task_intent(storage):
    storage.add_task(Task(title="Old task"))
    task_id = storage.get_tasks()[0]["id"]
    text = f"Updating task. [UPDATE_TASK: {task_id} | TITLE: New Title | COMPLETED: true]"
    response = process_ai_intent(text, storage)
    assert f"✅ **Task updated:** {task_id}" in response
    task = storage.get_tasks()[0]
    assert task["title"] == "New Title"
    assert task["completed"] is True

def test_delete_task_intent(storage):
    storage.add_task(Task(title="Remove me"))
    task_id = storage.get_tasks()[0]["id"]
    text = f"Removing. [DELETE_TASK: {task_id}]"
    response = process_ai_intent(text, storage)
    assert f"✅ **Task deleted:** {task_id}" in response
    assert len(storage.get_tasks()) == 0

def test_list_notes_with_ids(storage):
    storage.add_note(Note(content="Note with ID"))
    note_id = storage.get_notes()[0]["id"]
    text = "Show notes. [LIST_NOTES]"
    response = process_ai_intent(text, storage)
    assert f"[{note_id}]" in response
    assert "Note with ID" in response

def test_list_tasks_with_ids(storage):
    storage.add_task(Task(title="Task with ID"))
    task_id = storage.get_tasks()[0]["id"]
    text = "Show tasks. [LIST_TASKS]"
    response = process_ai_intent(text, storage)
    assert f"[{task_id}]" in response
    assert "Task with ID" in response

def test_complete_task_intent(storage):
    storage.add_task(Task(title="Finish homework"))
    text = "Done! [COMPLETE_TASK: Finish homework]"
    response = process_ai_intent(text, storage)
    assert "✅ **Task completed:** Finish homework" in response
    assert storage.get_tasks()[0]["completed"] is True

def test_search_intent(storage):
    storage.add_note(Note(content="Apple pie recipe"))
    text = "I'll look for that. [SEARCH: apple]"
    response = process_ai_intent(text, storage)
    assert "### Search Results for 'apple'" in response
    assert "Apple pie recipe" in response

def test_daily_brief_intent(storage):
    storage.add_task(Task(title="Buy eggs"))
    text = "Here is your update. [DAILY_BRIEF]"
    response = process_ai_intent(text, storage)
    assert "### Daily Briefing" in response
    assert "You have **1** pending tasks" in response
    assert "Buy eggs" in response
