import os
import json
import time
from notion_client import Client
from dotenv import load_dotenv

# Load credentials
load_dotenv("/Users/eleos/Documents/Command_Center/Protocols/.env")

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_TEAM_INBOX_ID")

notion = Client(auth=NOTION_TOKEN)

LOG_FILE = "usage_log.jsonl"
STATE_FILE = "notion_last_sync.txt"

def sync_to_notion():
    if not os.path.exists(LOG_FILE):
        return

    last_sync = 0.0
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            last_sync = float(f.read().strip())

    new_entries = []
    with open(LOG_FILE, "r") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get("timestamp", 0) > last_sync:
                    new_entries.append(entry)
            except: continue

    if not new_entries:
        print("No new entries to sync to Notion.")
        return

    print(f"Syncing {len(new_entries)} entries to Notion Database...")
    
    for entry in new_entries:
        date_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry['timestamp']))
        task_name = f"AI Usage: {entry['model']} ({date_str})"
        
        try:
            notion.pages.create(
                parent={"database_id": DATABASE_ID},
                properties={
                    "Task": {"title": [{"text": {"content": task_name}}]},
                    "Status": {"status": {"name": "Done"}},
                    "Agent Assigned": {"select": {"name": "Gemini"}}
                },
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {"text": {"content": f"Tokens: {entry['tokens']}\nSavings: ${entry['savings']:.4f}\nUser: {entry['user']}\nLatency: {entry.get('latency', 0)}s"}}
                            ]
                        }
                    }
                ]
            )
        except Exception as e:
            print(f"❌ Notion Error for entry {task_name}: {e}")

    # Update last sync
    with open(STATE_FILE, "w") as f:
        f.write(str(new_entries[-1]['timestamp']))

    print("✅ Notion sync complete.")

if __name__ == "__main__":
    sync_to_notion()
