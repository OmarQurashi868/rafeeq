from rafeeq.storage import StorageManager
from rafeeq.ai_client import AIClient
from rafeeq.tui import RafeeqApp

def main():
    # Initialize Storage
    storage = StorageManager()
    
    # Initialize AI Client
    try:
        ai = AIClient()
    except ValueError as e:
        print(f"Warning: {e}")
        ai = None

    # Launch TUI
    app = RafeeqApp(storage=storage, ai=ai)
    app.run()

if __name__ == "__main__":
    main()
