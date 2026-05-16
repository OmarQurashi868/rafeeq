import re
from typing import List, Dict, Any, Optional, Tuple
from rafeeq.storage import StorageManager, Note, Task

def execute_intents(text: str, storage: StorageManager) -> Tuple[str, List[str]]:
    # Regex patterns for markers
    note_pattern = r"\[SAVE_NOTE:\s*(.*?)\]"
    update_note_pattern = r"\[UPDATE_NOTE:\s*(.*?)\s*\|\s*(.*?)\]"
    delete_note_pattern = r"\[DELETE_NOTE:\s*(.*?)\]"
    
    task_pattern = r"\[ADD_TASK:\s*(.*?)(?:\s*\|\s*DUE:\s*(.*?))?\]"
    update_task_pattern = r"\[UPDATE_TASK:\s*(.*?)(?:\s*\|\s*TITLE:\s*(.*?))?(?:\s*\|\s*DUE:\s*(.*?))?(?:\s*\|\s*COMPLETED:\s*(.*?))?\]"
    delete_task_pattern = r"\[DELETE_TASK:\s*(.*?)\]"
    complete_task_pattern = r"\[COMPLETE_TASK:\s*(.*?)\]"
    
    list_notes_pattern = r"\[LIST_NOTES\]"
    list_tasks_pattern = r"\[LIST_TASKS\]"
    search_pattern = r"\[SEARCH:\s*(.*?)\]"
    brief_pattern = r"\[DAILY_BRIEF\]"
    task_brief_pattern = r"\[TASK_BRIEF\]"

    observations = []

    # Handle SAVE_NOTE
    notes = re.findall(note_pattern, text)
    for content in notes:
        new_note = storage.add_note(Note(content=content))
        observations.append(f"Note saved.")

    # Handle UPDATE_NOTE
    note_updates = re.findall(update_note_pattern, text)
    for selector, content in note_updates:
        ids = storage.resolve_indices("notes", selector)
        if not ids:
            observations.append(f"Error: Note [{selector}] not found.")
            continue
        for note_id in ids:
            if storage.update_note(note_id, content):
                observations.append(f"Note updated successfully.")
            else:
                observations.append(f"Error updating note.")

    # Handle DELETE_NOTE
    note_deletions = re.findall(delete_note_pattern, text)
    for selector in note_deletions:
        ids = storage.resolve_indices("notes", selector)
        if not ids:
            observations.append(f"Error: Note(s) [{selector}] not found.")
            continue
        for note_id in ids:
            if storage.delete_note(note_id):
                observations.append(f"Note deleted.")

    # Handle ADD_TASK
    tasks = re.findall(task_pattern, text)
    for title, due_date in tasks:
        new_task = storage.add_task(Task(title=title, due_date=due_date or None))
        msg = f"Task added: {title}"
        if due_date:
            msg += f" (Due: {due_date})"
        observations.append(msg)

    # Handle UPDATE_TASK
    task_updates = re.findall(update_task_pattern, text)
    for selector, title, due, completed_str in task_updates:
        ids = storage.resolve_indices("tasks", selector)
        if not ids:
            observations.append(f"Error: Task(s) [{selector}] not found.")
            continue
        
        title = title.strip() if title else None
        due = due.strip() if due else None
        completed = None
        if completed_str:
            completed = completed_str.strip().lower() == "true"
        
        for task_id in ids:
            if storage.update_task(task_id, title=title, due_date=due, completed=completed):
                observations.append(f"Task updated successfully.")
            else:
                observations.append(f"Error updating task.")

    # Handle DELETE_TASK
    task_deletions = re.findall(delete_task_pattern, text)
    for selector in task_deletions:
        ids = storage.resolve_indices("tasks", selector)
        if not ids:
            observations.append(f"Error: Task(s) [{selector}] not found.")
            continue
        for task_id in ids:
            if storage.delete_task(task_id):
                observations.append(f"Task deleted.")

    # Handle COMPLETE_TASK
    completions = re.findall(complete_task_pattern, text)
    for selector in completions:
        ids = storage.resolve_indices("tasks", selector)
        if not ids:
            # Try original behavior for title match if it doesn't look like a selector
            if storage.complete_task(selector):
                observations.append(f"Task marked as completed.")
            else:
                observations.append(f"Error: Task [{selector}] not found.")
            continue
            
        for task_id in ids:
            if storage.complete_task(task_id):
                observations.append(f"Task marked as completed.")

    # Handle LIST_NOTES
    if re.search(list_notes_pattern, text):
        indexed_notes = storage.get_indexed_items("notes")
        if not indexed_notes:
            observations.append("No notes found.")
        else:
            notes_list = "\n".join([f"- **{n['index']}.** {n['content']} *({n['timestamp'][:10]})*" for n in indexed_notes])     
            observations.append(f"Notes list:\n{notes_list}")

    # Handle LIST_TASKS
    if re.search(list_tasks_pattern, text):
        # Default to compact pending tasks for natural feel, 
        # unless 'all' is mentioned (but markers don't capture that yet)
        indexed_tasks = storage.get_indexed_items("tasks", include_completed=False)
        if not indexed_tasks:
            observations.append("No pending tasks found.")
        else:
            tasks_list = []
            for t in indexed_tasks:
                line = f"- **{t['index']}.** [{'x' if t['completed'] else ' '}] {t['title']}"
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
                # Use compact indexing for search results as well if possible, or just the global one
                full_notes = storage.get_indexed_items("notes")
                note_map = {n['id']: n['index'] for n in full_notes}
                res_text += "\nNotes:\n" + "\n".join([f"- **{note_map.get(n['id'], '?')}.** {n['content']}" for n in results["notes"]])
            if results["tasks"]:
                # Search results usually refer to PENDING tasks in the user's mind
                full_tasks = storage.get_indexed_items("tasks", include_completed=False)
                task_map = {t['id']: t['index'] for t in full_tasks}
                res_text += "\nTasks:\n" + "\n".join([f"- **{task_map.get(t['id'], '?')}.** [{'x' if t['completed'] else ' '}] {t['title']}" for t in results["tasks"]])
        observations.append(res_text)

    # Handle DAILY_BRIEF
    if re.search(brief_pattern, text):
        summary = storage.get_daily_summary()
        full_tasks = storage.get_indexed_items("tasks", include_completed=False)
        task_map = {t['id']: t['index'] for t in full_tasks}
        full_notes = storage.get_indexed_items("notes")
        note_map = {n['id']: n['index'] for n in full_notes}

        brief_text = f"Daily Briefing:\n"
        brief_text += f"Pending tasks: {summary['pending_tasks_count']}\n"
        if summary["pending_tasks"]:
            tasks_list = "\n".join([f"- **{task_map.get(t['id'], '?')}.** {t['title']}" for t in summary["pending_tasks"][:5]])
            brief_text += f"Key Tasks:\n{tasks_list}\n"
        if summary["recent_notes"]:
            notes_list = "\n".join([f"- **{note_map.get(n['id'], '?')}.** {n['content']}" for n in summary["recent_notes"][:5]])
            brief_text += f"Recent Notes:\n{notes_list}"
        observations.append(brief_text)

    # Handle TASK_BRIEF
    if re.search(task_brief_pattern, text):
        summary = storage.get_daily_summary()
        full_tasks = storage.get_indexed_items("tasks", include_completed=False)
        task_map = {t['id']: t['index'] for t in full_tasks}
        
        brief_text = f"Task Briefing:\n"
        brief_text += f"Pending tasks: {summary['pending_tasks_count']}\n"
        if summary["pending_tasks"]:
            tasks_list = "\n".join([f"- **{task_map.get(t['id'], '?')}.** {t['title']}" for t in summary["pending_tasks"]])
            brief_text += f"Current Pending Tasks:\n{tasks_list}"
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
    text = re.sub(task_brief_pattern, "", text)

    return text.strip(), observations
