import subprocess
import datetime
import logging
import threading
from typing import Optional

def _run_powershell(command: str):
    """Run a PowerShell command in the background."""
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", command],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        logging.error(f"PowerShell error: {e.stderr}")
    except Exception as e:
        logging.error(f"Failed to run PowerShell: {e}")

class WindowsNotificationManager:
    """Manages Windows Toast notifications and Scheduled Tasks via PowerShell."""

    def __init__(self):
        # Default PowerShell AppID for notifications
        self.app_id = "{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe"

    def schedule_reminder(self, task_id: str, title: str, due_date_str: str):
        """Schedule a Windows notification for a specific task."""
        try:
            # Parse due_date (Expected: YYYY-MM-DD HH:MM)
            due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d %H:%M")
            
            iso_date = due_date.strftime("%Y-%m-%dT%H:%M:%S")
            safe_title = title.replace("'", "''").replace('"', '`"')
            
            # Start with removing any existing reminder for this task
            ps_script = f"Unregister-ScheduledTask -TaskName 'Rafeeq_Task_{task_id}' -Confirm:$false -ErrorAction SilentlyContinue; "

            # Only add the new reminder if it's in the future
            if due_date >= datetime.datetime.now():
                # The PowerShell command that will be executed when the task triggers
                toast_cmd = (
                    f"[void][Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime]; "
                    f"[void][Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime]; "
                    f"$xml = [Windows.Data.Xml.Dom.XmlDocument]::new(); "
                    f"$xml.LoadXml(\\\"<toast><visual><binding template='ToastGeneric'>"
                    f"<text>Rafeeq Task Reminder</text><text>{safe_title}</text>"
                    f"</binding></visual></toast>\\\"); "
                    f"[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('{self.app_id}')"
                    f".Show([Windows.UI.Notifications.ToastNotification]::new($xml))"
                )

                # PowerShell script to register the scheduled task
                ps_script += (
                    f"$action = New-ScheduledTaskAction -Execute 'powershell.exe' "
                    f"-Argument '-NoProfile -WindowStyle Hidden -Command \"{toast_cmd}\"'; "
                    f"$trigger = New-ScheduledTaskTrigger -Once -At '{iso_date}'; "
                    f"Register-ScheduledTask -Action $action -Trigger $trigger "
                    f"-TaskName 'Rafeeq_Task_{task_id}' -Description 'Rafeeq Task Reminder' -Force"
                )

            # Run in a background thread to avoid blocking the TUI
            threading.Thread(target=_run_powershell, args=(ps_script,), daemon=True).start()
            
        except ValueError:
            logging.warning(f"Invalid due date format: {due_date_str}. Expected YYYY-MM-DD HH:MM")
        except Exception as e:
            logging.error(f"Failed to schedule reminder: {e}")

    def remove_reminder(self, task_id: str):
        """Remove a scheduled Windows notification."""
        ps_script = f"Unregister-ScheduledTask -TaskName 'Rafeeq_Task_{task_id}' -Confirm:$false -ErrorAction SilentlyContinue"
        threading.Thread(target=_run_powershell, args=(ps_script,), daemon=True).start()
