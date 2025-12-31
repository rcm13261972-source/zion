#!/usr/bin/env python3
"""
ZION INDEXER
============
The prophetic discernment engine for the Scripture Database.
This script pre-processes all verses to build layers of statistical
and pattern-based metadata, enabling deep, suggestive queries.

Architecture by Bobby. Code by Gemini 3.
"""

import sqlite3
import re
from pathlib import Path
from collections import Counter
import json
from collections import defaultdict

# --- PATHS ---
ZION_ENGINE_DIR = Path(__file__).parent
SCRIPTURE_DB = ZION_ENGINE_DIR / "scripture.db"

# --- LOGIC ---
def init_prophetic_db():
    """
    Upgrades the scripture.db with new tables for prophetic analysis.
    This function is idempotent and can be run safely multiple times.
    """
    print("💎 Initializing Prophetic Layer in scripture.db...")
    conn = sqlite3.connect(SCRIPTURE_DB)
    cursor = conn.cursor()

    # Table for word frequency analysis
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS word_stats (
            word TEXT PRIMARY KEY,
            count INTEGER NOT NULL,
            frequency REAL NOT NULL
        )
    ''')

    # Table for biblical number analysis
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS number_stats (
            number INTEGER PRIMARY KEY,
            count INTEGER NOT NULL,
            locations TEXT NOT NULL
        )
    ''')

    # Table to define the patterns we're looking for
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pattern_definitions (
            pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_name TEXT UNIQUE NOT NULL,
            description TEXT,
            keywords TEXT
        )
    ''')

    # Table to map which verses belong to which patterns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verse_to_pattern (
            verse_id INTEGER NOT NULL,
            pattern_id INTEGER NOT NULL,
            confidence REAL NOT NULL,
            FOREIGN KEY (verse_id) REFERENCES verses(id),
            FOREIGN KEY (pattern_id) REFERENCES pattern_definitions(pattern_id),
            UNIQUE(verse_id, pattern_id)
        )
    ''')
    
    conn.commit()
    print("✅ Prophetic Layer tables created/verified.")

    # Pre-populate known patterns
    known_patterns = {
        'INVERSION': ('The meek inheriting, the first being last.', 'blessed,poor,meek,mourn,last,first,servant,master'),
        'SOWING_REAPING': ('The algorithm of sowing and reaping, cause and effect.', 'seed,sow,ground,fruit,harvest,reap,water,plant'),
        'SACRIFICE': ('The pattern of sacrifice, blood, and redemption.', 'blood,altar,offering,lamb,sacrifice,slain,redeem'),
        'EXODUS': ('The pattern of liberation from bondage.', 'egypt,pharaoh,bondage,deliver,moses,exodus,freedom'),
        'JUDGMENT': ('The pattern of divine judgment and correction.', 'wrath,judgment,destroy,punish,wicked,sinners,fire')
    }
    for name, (desc, keywords) in known_patterns.items():
        cursor.execute("INSERT OR IGNORE INTO pattern_definitions (pattern_name, description, keywords) VALUES (?, ?, ?)", (name, desc, keywords))
    
    conn.commit()
    print("✓ Known patterns pre-populated.")
    conn.close()

def analyze_all_verses():
    """
    Analyzes every verse in the 'verses' table and populates
    word_stats, number_stats, and verse_to_pattern tables.
    """
    print("🧠 Analyzing all verses for patterns and statistics...")
    conn = sqlite3.connect(SCRIPTURE_DB)
    cursor = conn.cursor()

    # Clear previous analysis (for re-runs)
    cursor.execute("DELETE FROM word_stats")
    cursor.execute("DELETE FROM number_stats")
    cursor.execute("DELETE FROM verse_to_pattern")
    conn.commit()

    # Fetch all patterns and their keywords
    cursor.execute("SELECT pattern_id, pattern_name, keywords FROM pattern_definitions")
    pattern_defs = {row[0]: {'name': row[1], 'keywords': [k.strip() for k in row[2].split(',')]} for row in cursor.fetchall()}

    # Fetch all verses
    cursor.execute("SELECT id, text FROM verses")
    all_verses = cursor.fetchall()
    
    total_words = 0
    word_counts = Counter()
    number_locations = defaultdict(list)

    print(f"Processing {len(all_verses)} verses...")
    for verse_id, verse_text in all_verses:
        clean_text = re.sub(r'[^\w\s]', '', verse_text).lower()
        words = clean_text.split()
        total_words += len(words)
        word_counts.update(words)

        # Extract numbers and their locations
        for match in re.finditer(r'\b(\d+)\b', verse_text):
            num = int(match.group(1))
            number_locations[num].append(verse_id) # Store verse_id where number appears

        # Detect patterns in the verse
        for p_id, p_def in pattern_defs.items():
            score = 0
            for keyword in p_def['keywords']:
                if re.search(r'\b' + re.escape(keyword) + r'\b', clean_text):
                    score += 1
            
            if score > 0:
                confidence = score / len(p_def['keywords']) # Simple confidence
                cursor.execute("INSERT OR IGNORE INTO verse_to_pattern (verse_id, pattern_id, confidence) VALUES (?, ?, ?)",
                               (verse_id, p_id, confidence))
    
    # Insert word_stats
    for word, count in word_counts.items():
        frequency = count / total_words
        cursor.execute("INSERT OR REPLACE INTO word_stats (word, count, frequency) VALUES (?, ?, ?)",
                       (word, count, frequency))
    
    # Insert number_stats
    for num, v_ids in number_locations.items():
        # Store locations as a JSON string
        cursor.execute("INSERT OR REPLACE INTO number_stats (number, count, locations) VALUES (?, ?, ?)",
                       (num, len(v_ids), json.dumps(v_ids)))

    conn.commit()
    print(f"✅ Analysis complete. {len(word_counts)} unique words, {len(number_locations)} unique numbers indexed.")
    conn.close()


def main():
    print("Zion Indexer: Initializing database structure.")
    init_prophetic_db()
    
    # Add an argument to run the analysis
    import argparse
    parser = argparse.ArgumentParser(description='Zion Indexer - Prophetic Discernment Engine')
    parser.add_argument('--init', action='store_true', help='Initialize database tables (default if no other args)')
    parser.add_argument('--analyze', action='store_true', help='Analyze all verses and populate stats/patterns tables')
    
    args = parser.parse_args()

    if args.analyze:
        analyze_all_verses()
    else:
        # Default behavior is init if no other action is specified
        if not args.init: # Only re-init if not explicitly asked
            init_prophetic_db()
        else: # If --init is passed explicitly, only do init
            init_prophetic_db()

    print("\nNext steps:")
    print("1. Implement `generate_suggestive_connections()` for deep analysis.")

if __name__ == "__main__":
    main()