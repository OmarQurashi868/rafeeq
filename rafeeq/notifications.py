import subprocess
import datetime
import logging
import threading
import os
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
        self.scripts_dir = os.path.join(os.getcwd(), ".rafeeq_scripts")
        if not os.path.exists(self.scripts_dir):
            os.makedirs(self.scripts_dir)

    def schedule_reminder(self, task_id: str, title: str, due_date_str: str):
        """Schedule a Windows notification for a specific task."""
        try:
            # Parse due_date (Support both YYYY-MM-DD HH:MM and YYYY-MM-DD HH:MM:SS)
            due_date = None
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
                try:
                    due_date = datetime.datetime.strptime(due_date_str, fmt)
                    break
                except ValueError:
                    continue
            
            if not due_date:
                raise ValueError(f"Invalid format: {due_date_str}")
            
            iso_date = due_date.strftime("%Y-%m-%dT%H:%M:%S")
            safe_title = title.replace("'", "''")
            
            # Create a dedicated .ps1 script for this notification to avoid escaping hell
            script_path = os.path.join(self.scripts_dir, f"notify_{task_id}.ps1")
            toast_script = (
                f"[void][Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime]\n"
                f"[void][Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime]\n"
                f"$xml = [Windows.Data.Xml.Dom.XmlDocument]::new()\n"
                f"$xml.LoadXml('<toast><visual><binding template=''ToastGeneric''>"
                f"<text>Rafeeq Task Reminder</text><text>{safe_title}</text>"
                f"</binding></visual></toast>')\n"
                f"$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)\n"
                f"[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('{self.app_id}').Show($toast)\n"
            )
            
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(toast_script)

            # Start with removing any existing reminder for this task
            ps_script = f"Unregister-ScheduledTask -TaskName 'Rafeeq_Task_{task_id}' -Confirm:$false -ErrorAction SilentlyContinue; "

            # Only add the new reminder if it's in the future
            if due_date > datetime.datetime.now():
                ps_script += (
                    f"$action = New-ScheduledTaskAction -Execute 'powershell.exe' "
                    f"-Argument '-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File \"{script_path}\"'; "
                    f"$trigger = New-ScheduledTaskTrigger -Once -At '{iso_date}'; "
                    f"Register-ScheduledTask -Action $action -Trigger $trigger "
                    f"-TaskName 'Rafeeq_Task_{task_id}' -Description 'Rafeeq Task Reminder' -Force"
                )

            # Run in a background thread to avoid blocking the TUI
            threading.Thread(target=_run_powershell, args=(ps_script,), daemon=True).start()
            
        except ValueError as e:
            logging.warning(f"Invalid due date: {e}. Expected YYYY-MM-DD HH:MM[:SS]")
        except Exception as e:
            logging.error(f"Failed to schedule reminder: {e}")

    def remove_reminder(self, task_id: str):
        """Remove a scheduled Windows notification."""
        ps_script = f"Unregister-ScheduledTask -TaskName 'Rafeeq_Task_{task_id}' -Confirm:$false -ErrorAction SilentlyContinue"
        threading.Thread(target=_run_powershell, args=(ps_script,), daemon=True).start()
        
        # Also try to remove the script file
        script_path = os.path.join(self.scripts_dir, f"notify_{task_id}.ps1")
        if os.path.exists(script_path):
            try:
                os.remove(script_path)
            except Exception:
                pass
