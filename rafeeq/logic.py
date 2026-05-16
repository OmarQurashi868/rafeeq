import re
from typing import List, Dict, Any, Optional, Tuple
from rafeeq.storage import StorageManager, Note, Task

def execute_intents(text: str, storage: StorageManager) -> Tuple[str, List[str]]:
    # Regex patterns for markers
    note_pattern = r"\[SAVE_NOTE:\s*(.*?)\]"
    update_note_pattern = r"\[UPDATE_NOTE:\s*([a-f0-9]{6})\s*\|\s*(.*?)\]"
    delete_note_pattern = r"\[DELETE_NOTE:\s*([a-f0-9]{6})\]"
    
    task_pattern = r"\[ADD_TASK:\s*(.*?)(?:\s*\|\s*DUE:\s*(.*?))?\]"
    update_task_pattern = r"\[UPDATE_TASK:\s*([a-f0-9]{6})(?:\s*\|\s*TITLE:\s*(.*?))?(?:\s*\|\s*DUE:\s*(.*?))?(?:\s*\|\s*COMPLETED:\s*(.*?))?\]"
    delete_task_pattern = r"\[DELETE_TASK:\s*([a-f0-9]{6})\]"
    complete_task_pattern = r"\[COMPLETE_TASK:\s*(.*?)\]"
    
    list_notes_pattern = r"\[LIST_NOTES\]"
    list_tasks_pattern = r"\[LIST_TASKS\]"
    search_pattern = r"\[SEARCH:\s*(.*?)\]"
    brief_pattern = r"\[DAILY_BRIEF\]"

    observations = []

    # Handle SAVE_NOTE
    notes = re.findall(note_pattern, text)
    for content in notes:
        new_note = storage.add_note(Note(content=content))
        observations.append(f"Note saved with ID [{new_note.id}]")

    # Handle UPDATE_NOTE
    note_updates = re.findall(update_note_pattern, text)
    for note_id, content in note_updates:
        if storage.update_note(note_id, content):
            observations.append(f"Note [{note_id}] updated successfully.")
        else:
            observations.append(f"Error: Note [{note_id}] not found.")

    # Handle DELETE_NOTE
    note_deletions = re.findall(delete_note_pattern, text)
    for note_id in note_deletions:
        if storage.delete_note(note_id):
            observations.append(f"Note [{note_id}] deleted.")
        else:
            observations.append(f"Error: Note [{note_id}] not found.")

    # Handle ADD_TASK
    tasks = re.findall(task_pattern, text)
    for title, due_date in tasks:
        new_task = storage.add_task(Task(title=title, due_date=due_date or None))
        msg = f"Task added with ID [{new_task.id}]: {title}"
        if due_date:
            msg += f" (Due: {due_date})"
        observations.append(msg)

    # Handle UPDATE_TASK
    task_updates = re.findall(update_task_pattern, text)
    for task_id, title, due, completed_str in task_updates:
        title = title.strip() if title else None
        due = due.strip() if due else None
        completed = None
        if completed_str:
            completed = completed_str.strip().lower() == "true"
        
        if storage.update_task(task_id, title=title, due_date=due, completed=completed):
            observations.append(f"Task [{task_id}] updated successfully.")
        else:
            observations.append(f"Error: Task [{task_id}] not found.")

    # Handle DELETE_TASK
    task_deletions = re.findall(delete_task_pattern, text)
    for task_id in task_deletions:
        if storage.delete_task(task_id):
            observations.append(f"Task [{task_id}] deleted.")
        else:
            observations.append(f"Error: Task [{task_id}] not found.")

    # Handle COMPLETE_TASK
    completions = re.findall(complete_task_pattern, text)
    for identifier in completions:
        if storage.complete_task(identifier):
            observations.append(f"Task [{identifier}] marked as completed.")
        else:
            observations.append(f"Error: Task [{identifier}] not found.")

    # Handle LIST_NOTES
    if re.search(list_notes_pattern, text):
        all_notes = storage.get_notes()
        if not all_notes:
            observations.append("No notes found.")
        else:
            notes_list = "\n".join([f"- `[{n['id']}]` {n['content']} *({n['timestamp'][:10]})*" for n in all_notes])     
            observations.append(f"Notes list:\n{notes_list}")

    # Handle LIST_TASKS
    if re.search(list_tasks_pattern, text):
        all_tasks = storage.get_tasks()
        if not all_tasks:
            observations.append("No tasks found.")
        else:
            tasks_list = []
            for t in all_tasks:
                line = f"- `[{t['id']}]` [{'x' if t['completed'] else ' '}] {t['title']}"
                if t.get('due_date'):
                    line += f" * (Due: {t['due_date']})*"
                tasks_list.append(line)
            observations.append(f"Tasks list:\n" + "\n".join(tasks_list))

    # Handle SEARCH
    search_queries = re.findall(search_pattern, text)
    for query in search_queries:
        results = storage.search(query)
        res_text = f"Search results for '{query}':"
        if not results["notes"] and not results["tasks"]:
            res_text += " No results found."
        else:
            if results["notes"]:
                res_text += "\nNotes:\n" + "\n".join([f"- `[{n['id']}]` {n['content']}" for n in results["notes"]])
            if results["tasks"]:
                res_text += "\nTasks:\n" + "\n".join([f"- `[{t['id']}]` [{'x' if t['completed'] else ' '}] {t['title']}" for t in results["tasks"]])
        observations.append(res_text)

    # Handle DAILY_BRIEF
    if re.search(brief_pattern, text):
        summary = storage.get_daily_summary()
        brief_text = f"Daily Briefing:\n"
        brief_text += f"Pending tasks: {summary['pending_tasks_count']}\n"
        if summary["pending_tasks"]:
            tasks_list = "\n".join([f"- `[{t['id']}]` {t['title']}" for t in summary["pending_tasks"][:5]])
            brief_text += f"Key Tasks:\n{tasks_list}\n"
        if summary["recent_notes"]:
            notes_list = "\n".join([f"- `[{n['id']}]` {n['content']}" for n in summary["recent_notes"][:5]])
            brief_text += f"Recent Notes:\n{notes_list}"
        observations.append(brief_text)

    # Clean up markers from the final text
    text = re.sub(note_pattern, "", text)
    text = re.sub(update_note_pattern, "", text)
    text = re.sub(delete_note_pattern, "", text)
    text = re.sub(task_pattern, "", text)
    text = re.sub(update_task_pattern, "", text)
    text = re.sub(delete_task_pattern, "", text)
    text = re.sub(complete_task_pattern, "", text)
    text = re.sub(list_notes_pattern, "", text)
    text = re.sub(list_tasks_pattern, "", text)
    text = re.sub(search_pattern, "", text)
    text = re.sub(brief_pattern, "", text)

    return text.strip(), observations
