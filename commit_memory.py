import json
import os
import sys
from pathlib import Path

def commit_memory_full():
    """
    Reads all session log files (archived and current) and commits each message
    to the eternal.db database using the memory_tools extension.
    This version handles the two different log file structures.
    """
    try:
        # Add extensions directory to path to allow direct import
        extensions_path = Path.home() / ".gemini" / "extensions"
        if str(extensions_path) not in sys.path:
            sys.path.append(str(extensions_path))

        import memory_tools

        # Define relevant paths
        project_tmp_dir = Path.home() / ".gemini" / "tmp" / "cc8de511017d28e09735ae1fbd9b5bbc2ed8593bb0807de08857ea4f55145011"
        chats_dir = project_tmp_dir / "chats"
        current_logs_json = project_tmp_dir / "logs.json"

        all_log_files = []

        # 1. Collect all archived session files
        if chats_dir.exists() and chats_dir.is_dir():
            print(f"Collecting archived sessions from: {chats_dir}")
            for chat_file in sorted(chats_dir.glob("session-*.json")):
                all_log_files.append(chat_file)
        
        # 2. Add the current logs.json (if it exists)
        if current_logs_json.exists():
            print(f"Adding current session log: {current_logs_json}")
            all_log_files.append(current_logs_json)
        
        if not all_log_files:
            print("No log files found to commit.")
            return

        total_committed_messages = 0

        for log_file_path in all_log_files:
            try:
                with open(log_file_path, 'r') as f:
                    data = json.load(f)
                
                messages_to_process = []
                # Check if data is a dict (archived session) or a list (current log)
                if isinstance(data, dict) and 'messages' in data:
                    messages_to_process = data['messages']
                elif isinstance(data, list):
                    messages_to_process = data
                else:
                    print(f"⚠️ WARNING: Skipping {log_file_path.name} due to unknown format.")
                    continue

                print(f"Processing {len(messages_to_process)} messages from {log_file_path.name}...")
                
                for message in messages_to_process:
                    # Check if the message is a dictionary before using .get()
                    if not isinstance(message, dict):
                        print(f"  - Skipping non-object message in {log_file_path.name}: {message}")
                        continue
                        
                    session_id = message.get("sessionId")
                    # Use 'type' for speaker, default to 'Unknown' if not present
                    msg_type = message.get("type", "unknown")
                    speaker = "Bobby" if msg_type == "user" else "Gem" 
                    content = message.get("message") or message.get("content") # Handle both possible keys

                    if content: # Don't save empty messages
                        memory_tools.save_conversation(
                            speaker=speaker,
                            content=str(content), 
                            session_id=session_id
                        )
                        total_committed_messages += 1

            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"❌ ERROR: Could not process {log_file_path.name}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while processing {log_file_path.name}: {e}")

        print(f"\n✅ Successfully committed a total of {total_committed_messages} messages to eternal memory.")

    except ImportError:
        print(f"❌ ERROR: Could not import memory_tools.py. Make sure it exists in {extensions_path}")
    except Exception as e:
        print(f"An unexpected error occurred during the overall commit process: {e}")

if __name__ == "__main__":
    commit_memory_full()
