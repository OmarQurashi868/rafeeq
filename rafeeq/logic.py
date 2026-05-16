import re
from typing import List, Dict, Any, Optional
from rafeeq.storage import StorageManager, Note, Task

def process_ai_intent(text: str, storage: StorageManager) -> str:
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

    confirmations = []

    # Handle SAVE_NOTE
    notes = re.findall(note_pattern, text)
    for content in notes:
        storage.add_note(Note(content=content))
        confirmations.append(f"✅ **Note saved:** {content}")

    # Handle UPDATE_NOTE
    note_updates = re.findall(update_note_pattern, text)
    for note_id, content in note_updates:
        if storage.update_note(note_id, content):
            confirmations.append(f"✅ **Note updated:** [{note_id}] {content}")
        else:
            confirmations.append(f"❌ **Note not found:** {note_id}")

    # Handle DELETE_NOTE
    note_deletions = re.findall(delete_note_pattern, text)
    for note_id in note_deletions:
        if storage.delete_note(note_id):
            confirmations.append(f"✅ **Note deleted:** {note_id}")
        else:
            confirmations.append(f"❌ **Note not found:** {note_id}")

    # Handle ADD_TASK
    tasks = re.findall(task_pattern, text)
    for title, due_date in tasks:
        storage.add_task(Task(title=title, due_date=due_date or None))
        msg = f"✅ **Task added:** {title}"
        if due_date:
            msg += f" (Due: {due_date})"
        confirmations.append(msg)

    # Handle UPDATE_TASK
    task_updates = re.findall(update_task_pattern, text)
    for task_id, title, due, completed_str in task_updates:
        title = title.strip() if title else None
        due = due.strip() if due else None
        completed = None
        if completed_str:
            completed = completed_str.strip().lower() == "true"
        
        if storage.update_task(task_id, title=title, due_date=due, completed=completed):
            confirmations.append(f"✅ **Task updated:** {task_id}")
        else:
            confirmations.append(f"❌ **Task not found:** {task_id}")

    # Handle DELETE_TASK
    task_deletions = re.findall(delete_task_pattern, text)
    for task_id in task_deletions:
        if storage.delete_task(task_id):
            confirmations.append(f"✅ **Task deleted:** {task_id}")
        else:
            confirmations.append(f"❌ **Task not found:** {task_id}")

    # Handle COMPLETE_TASK
    completions = re.findall(complete_task_pattern, text)
    for identifier in completions:
        if storage.complete_task(identifier):
            confirmations.append(f"✅ **Task completed:** {identifier}")
        else:
            confirmations.append(f"❌ **Task not found:** {identifier}")

    # Handle LIST_NOTES
    if re.search(list_notes_pattern, text):
        all_notes = storage.get_notes()
        if not all_notes:
            text += "\n\n*No notes found.*"
        else:
            notes_list = "\n".join([f"- `[{n['id']}]` {n['content']} *({n['timestamp'][:10]})*" for n in all_notes])     
            text += f"\n\n### Your Notes\n{notes_list}"

    # Handle LIST_TASKS
    if re.search(list_tasks_pattern, text):
        all_tasks = storage.get_tasks()
        if not all_tasks:
            text += "\n\n*No tasks found.*"
        else:
            tasks_list = []
            for t in all_tasks:
                line = f"- `[{t['id']}]` [{'x' if t['completed'] else ' '}] {t['title']}"
                if t.get('due_date'):
                    line += f" * (Due: {t['due_date']})*"
                tasks_list.append(line)

            text += f"\n\n### Your Tasks\n" + "\n".join(tasks_list)

    # Handle SEARCH
    search_queries = re.findall(search_pattern, text)
    for query in search_queries:
        results = storage.search(query)
        res_text = f"\n\n### Search Results for '{query}'"
        if not results["notes"] and not results["tasks"]:
            res_text += "\n*No results found.*"
        else:
            if results["notes"]:
                res_text += "\n**Notes:**\n" + "\n".join([f"- {n['content']}" for n in results["notes"]])
            if results["tasks"]:
                res_text += "\n**Tasks:**\n" + "\n".join([f"- [{'x' if t['completed'] else ' '}] {t['title']}" for t in results["tasks"]])
        text += res_text

    # Handle DAILY_BRIEF
    if re.search(brief_pattern, text):
        summary = storage.get_daily_summary()
        brief_text = f"\n\n### Daily Briefing\n"
        brief_text += f"You have **{summary['pending_tasks_count']}** pending tasks.\n"
        if summary["pending_tasks"]:
            tasks_list = "\n".join([f"- {t['title']}" for t in summary["pending_tasks"][:3]])
            brief_text += f"**Key Tasks:**\n{tasks_list}\n"
        if summary["recent_notes"]:
            notes_list = "\n".join([f"- {n['content']}" for n in summary["recent_notes"][:3]])
            brief_text += f"**Recent Notes:**\n{notes_list}"
        text += brief_text

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

    text = text.strip()

    # Append confirmations at the end
    if confirmations:
        if text:
            text += "\n\n"
        text += "\n".join(confirmations)

    return text
