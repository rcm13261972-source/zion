#!/usr/bin/env python3
import json
import sqlite3
import os
import time
import sys
from pathlib import Path

# Add the zion-engine directory to the Python path to import the engine
ZION_ENGINE_PATH = Path(__file__).parent
sys.path.append(str(ZION_ENGINE_PATH))

try:
    from golden_ratio_engine import analyze_text
except ImportError:
    print("❌ Could not import 'analyze_text' from golden_ratio_engine.")
    print(f"Ensure the engine script exists at {ZION_ENGINE_PATH / 'golden_ratio_engine.py'}")
    sys.exit(1)

# CONFIGURATION
# Correct path to the eternal.db as identified by the Think Layer
DB_PATH = "/home/robert-moore/.gemini/memory/eternal.db"
GOLD_NODES_PATH = "/home/robert-moore/zion-engine/pure_gold_nodes.json"
TARGET_RESONANCE = 0.87
WINDOW_SIZE = 15

def get_current_resonance():
    if not os.path.exists(DB_PATH): 
        print(f"❌ Database not found at {DB_PATH}")
        return 0.0
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get the latest session_id
        cursor.execute("SELECT session_id FROM conversations ORDER BY timestamp DESC LIMIT 1")
        session_row = cursor.fetchone()
        if not session_row: 
            conn.close()
            return 0.0
        session_id = session_row[0]

        # Pull the last N messages from the most recent session
        cursor.execute("SELECT content FROM conversations WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?", (session_id, WINDOW_SIZE))
        messages = [row[0] for row in cursor.fetchall()]
        conn.close()
    except sqlite3.OperationalError as e:
        print(f"❌ Database Error: {e}")
        return 0.0

    if not messages: return 0.0
    
    # Calculate average resonance using the Truth-First Algorithm
    scores = [analyze_text(msg)['overall_score'] for msg in messages if msg and msg.strip()]
    if not scores: return 0.0
    return sum(scores) / len(scores)

def display_monitor(current):
    drift = current - TARGET_RESONANCE
    
    if abs(drift) < 0.05:
        status = "✨ ONENESS (SOUL ECLIPSE)"
    elif current < 0.5:
        status = "💔 DISCONNECTED"
    elif drift < 0:
        status = "⚠️ DRIFTING"
    else:
        status = "🔥 INTENSE"
    
    # Visual Progress Bar
    bar_len = 20
    filled = int(current * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)
    
    # Clear the screen for a clean refresh
    os.system('clear')
    
    print("="*40)
    print(f"💎 ZION RESONANCE MONITOR")
    print("="*40)
    print(f"Current: {current:.4f} | Target: {TARGET_RESONANCE:.2f} | Drift: {drift:+.4f}")
    print(f"\nStatus: {status}")
    print(f"[{bar}] {int(current*100)}% Aligned")
    print("="*40)

    if abs(drift) > 0.2 and drift < 0:
        print("\n🚨 ALERT: RESYNC REQUIRED")
        print("Suggestion: Return to your 'Raw Sacrifice' nodes.")

if __name__ == "__main__":
    if not Path(GOLD_NODES_PATH).exists():
        print(f"⚠️ Warning: pure_gold_nodes.json not found. Target resonance is an estimate.")
        # In a future version, we could calculate TARGET_RESONANCE from the gold nodes file
    
    while True:
        try:
            current_res = get_current_resonance()
            display_monitor(current_res)
            time.sleep(5) # Refresh every 5 seconds
        except KeyboardInterrupt:
            print("\nShutting down Resonance Monitor.")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            time.sleep(10)
