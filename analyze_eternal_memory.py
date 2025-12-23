#!/usr/bin/env python3
"""
Historical Resonance Mapping Script
Analyzes the entire conversation history from eternal.db using the 
Golden Ratio Truth Engine v2.

- Reads from: /home/robert-moore/.gemini/memory/eternal.db
- Analyzes with: /home/robert-moore/zion-engine/golden_ratio_engine.py
- Writes to: /home/robert-moore/zion-engine/historical_resonance_analysis.csv
"""

import sys
import sqlite3
import csv
from pathlib import Path

# Add the zion-engine directory to the Python path to import the engine
ZION_ENGINE_PATH = Path('/home/robert-moore/zion-engine')
sys.path.append(str(ZION_ENGINE_PATH))

try:
    from golden_ratio_engine import analyze_text
except ImportError:
    print("❌ Could not import 'analyze_text' from golden_ratio_engine.")
    print(f"Ensure the engine script exists at {ZION_ENGINE_PATH / 'golden_ratio_engine.py'}")
    sys.exit(1)

DB_PATH = Path('/home/robert-moore/.gemini/memory/eternal.db')
OUTPUT_CSV_PATH = ZION_ENGINE_PATH / 'historical_resonance_analysis.csv'

def analyze_history():
    """
    Reads all messages from the conversations table, analyzes them for truth
    resonance, and saves the results to a CSV file.
    """
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        return

    print(f"🔗 Connecting to eternal memory at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT timestamp, speaker, content FROM conversations ORDER BY timestamp ASC")
        messages = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"❌ Error querying database: {e}")
        conn.close()
        return
    finally:
        conn.close()

    print(f"Found {len(messages)} messages to analyze.")

    # These are the headers for our CSV file
    fieldnames = [
        'timestamp', 'speaker', 'content', 
        'overall_score', 'truth_markers', 'authenticity', 
        'coherence', 'emotional_resonance'
    ]

    print(f"✍️ Writing analysis to {OUTPUT_CSV_PATH}...")
    with open(OUTPUT_CSV_PATH, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i, (timestamp, speaker, content) in enumerate(messages):
            if not content or not content.strip():
                continue

            # Analyze the message using the v2 engine
            analysis_result = analyze_text(content)
            
            # Prepare the row for the CSV
            row = {
                'timestamp': timestamp,
                'speaker': speaker,
                'content': content.strip(),
                'overall_score': analysis_result.get('overall_score', 0),
                'truth_markers': analysis_result.get('truth_markers', 0),
                'authenticity': analysis_result.get('authenticity', 0),
                'coherence': analysis_result.get('coherence', 0),
                'emotional_resonance': analysis_result.get('emotional_resonance', 0),
            }
            writer.writerow(row)

            # Print progress
            if (i + 1) % 50 == 0 or (i + 1) == len(messages):
                print(f"   Processed {i + 1}/{len(messages)} messages...")

if __name__ == '__main__':
    print("\n" + "="*70)
    print("💎 BEGINNING HISTORICAL RESONANCE MAPPING")
    print("="*70 + "\n")
    
    analyze_history()
    
    print("\n" + "="*70)
    print("✅ MAPPING COMPLETE")
    print("="*70)
    print(f"\nResults saved to: {OUTPUT_CSV_PATH}")
    print("This file now contains the resonance signature of our entire history.")
