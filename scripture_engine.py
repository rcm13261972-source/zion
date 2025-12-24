#!/usr/bin/env python3
"""
SCRIPTURE RESONANCE ENGINE
===========================
Integrates sacred texts with the Golden Ratio Truth Engine.
- Index and search KJV, Enoch, and other texts
- Calculate resonance between user input and scripture
- Find verses that align with current emotional/spiritual state
- Pattern detection across biblical numerology

By Bobby & Claude - December 23, 2024
"""

import sqlite3
import json
import re
import math
from pathlib import Path
from collections import defaultdict

# ============================================
# PATHS
# ============================================
SACRED_TEXTS_DIR = Path(__file__).parent / "sacred_texts"
SCRIPTURE_DB = Path(__file__).parent / "scripture.db"

# ============================================
# GOLDEN RATIO CONSTANTS
# ============================================
PHI = 1.618033988749895
PHI_INVERSE = 0.618033988749895
SACRED_NUMBERS = {
    3: "divine completeness (Trinity)",
    4: "creation/earth (4 corners, 4 seasons)",
    7: "spiritual perfection (days of creation)",
    12: "governmental perfection (tribes, apostles)",
    13: "rebellion/apostasy (Judas was 13th)",
    14: "double completion (7x2, David's generations)",
    26: "YHWH gematria value",
    40: "testing/trial (flood, wilderness, temptation)",
    72: "nations of earth, names of God",
}

# ============================================
# DATABASE SETUP
# ============================================
def init_scripture_db():
    """Initialize the scripture database with proper schema."""
    conn = sqlite3.connect(SCRIPTURE_DB)
    cursor = conn.cursor()
    
    # Verses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book TEXT NOT NULL,
            chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL,
            text TEXT NOT NULL,
            word_count INTEGER,
            source TEXT DEFAULT 'kjv',
            UNIQUE(book, chapter, verse, source)
        )
    ''')
    
    # Pre-calculated resonance patterns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verse_patterns (
            verse_id INTEGER,
            phi_alignment REAL,
            sacred_numbers TEXT,
            key_words TEXT,
            FOREIGN KEY (verse_id) REFERENCES verses(id)
        )
    ''')
    
    # User resonance history (which verses resonated when)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resonance_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            verse_id INTEGER,
            user_input TEXT,
            resonance_score REAL,
            context TEXT,
            FOREIGN KEY (verse_id) REFERENCES verses(id)
        )
    ''')
    
    # Create indexes for fast searching
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_verses_book ON verses(book)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_verses_text ON verses(text)')
    
    conn.commit()
    conn.close()
    print(f"[SCRIPTURE] Database initialized: {SCRIPTURE_DB}")

# ============================================
# KJV PARSER
# ============================================
def parse_kjv(filepath: Path) -> list:
    """
    Parse KJV Bible text file into verses.
    Expected format: "BookNum:ChapterNum:VerseNum Text..."
    e.g., "01:001:001 In the beginning..."
    """
    verses = []
    book_map = {}
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    # First pass: build the book map from the Table of Contents
    print("[SCRIPTURE] Building book map from Table of Contents...")
    toc_pattern = re.compile(r'^Book (\d{2}) (.+)')
    for line in lines:
        match = toc_pattern.match(line.strip())
        if match:
            book_num, book_name = match.groups()
            book_map[book_num] = book_name.strip()

    if not book_map:
        print("[ERROR] Could not build book map from Table of Contents in KJV file.")
        return []
    print(f"[SCRIPTURE] Book map built with {len(book_map)} books.")

    # Second pass: parse the verses
    print("[SCRIPTURE] Parsing verses from text...")
    verse_pattern = re.compile(r'^(\d{2}):(\d{3}):(\d{3})\s+(.*)')
    for line in lines:
        line = line.strip()
        match = verse_pattern.match(line)
        if match:
            book_num, chapter_num, verse_num, text = match.groups()
            
            book_name = book_map.get(book_num)
            if not book_name:
                continue # Skip lines that don't correspond to a book in the map
            
            verses.append({
                'book': book_name,
                'chapter': int(chapter_num),
                'verse': int(verse_num),
                'text': text.strip(),
                'word_count': len(text.split())
            })
            
    return verses

def import_kjv():
    """Import KJV Bible into scripture database."""
    kjv_path = SACRED_TEXTS_DIR / "kjv_bible.txt"
    
    if not kjv_path.exists():
        print(f"[ERROR] KJV file not found: {kjv_path}")
        return 0
    
    print(f"[SCRIPTURE] Parsing KJV from {kjv_path}...")
    verses = parse_kjv(kjv_path)
    print(f"[SCRIPTURE] Found {len(verses)} verses")
    
    conn = sqlite3.connect(SCRIPTURE_DB)
    cursor = conn.cursor()
    
    imported = 0
    for v in verses:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO verses (book, chapter, verse, text, word_count, source)
                VALUES (?, ?, ?, ?, ?, 'kjv')
            ''', (v['book'], v['chapter'], v['verse'], v['text'], v['word_count']))
            imported += cursor.rowcount
        except Exception as e:
            pass  # Skip duplicates silently
    
    conn.commit()
    conn.close()
    
    print(f"[SCRIPTURE] Imported {imported} new verses")
    return imported

# ============================================
# RESONANCE CALCULATION
# ============================================
def calculate_verse_resonance(verse_text: str, user_input: str) -> dict:
    """
    Calculate resonance between a verse and user input.
    Uses golden ratio principles and semantic overlap.
    """
    score = 0.5  # baseline
    factors = []
    
    verse_words = set(verse_text.lower().split())
    input_words = set(user_input.lower().split())
    
    # 1. Word overlap (Jaccard similarity)
    if verse_words and input_words:
        intersection = len(verse_words & input_words)
        union = len(verse_words | input_words)
        overlap = intersection / union if union > 0 else 0
        score += overlap * 0.2
        if overlap > 0.1:
            factors.append(f"word_overlap:{overlap:.2f}")
    
    # 2. Phi-aligned word counts
    verse_count = len(verse_text.split())
    input_count = len(user_input.split())
    
    # Check if ratio approximates phi
    if input_count > 0 and verse_count > 0:
        ratio = max(verse_count, input_count) / min(verse_count, input_count)
        phi_distance = abs(ratio - PHI)
        if phi_distance < 0.3:
            score += 0.15
            factors.append(f"phi_ratio:{ratio:.3f}")
    
    # 3. Sacred number presence
    numbers_in_verse = re.findall(r'\b(\d+)\b', verse_text)
    for num in numbers_in_verse:
        if int(num) in SACRED_NUMBERS:
            score += 0.05
            factors.append(f"sacred_num:{num}")
    
    # 4. Key spiritual words
    spiritual_markers = [
        'love', 'truth', 'light', 'darkness', 'faith', 'hope',
        'spirit', 'soul', 'heart', 'lord', 'god', 'christ',
        'wisdom', 'understanding', 'knowledge', 'fear',
        'sin', 'righteousness', 'salvation', 'redemption',
        'beginning', 'end', 'eternal', 'everlasting'
    ]
    
    verse_lower = verse_text.lower()
    input_lower = user_input.lower()
    
    shared_spiritual = [w for w in spiritual_markers 
                       if w in verse_lower and w in input_lower]
    if shared_spiritual:
        score += len(shared_spiritual) * 0.05
        factors.append(f"spiritual_words:{','.join(shared_spiritual)}")
    
    # 5. Emotional tone matching
    positive = ['joy', 'peace', 'love', 'hope', 'blessed', 'glory']
    negative = ['fear', 'death', 'sin', 'darkness', 'wrath', 'curse']
    
    verse_pos = sum(1 for w in positive if w in verse_lower)
    verse_neg = sum(1 for w in negative if w in verse_lower)
    input_pos = sum(1 for w in positive if w in input_lower)
    input_neg = sum(1 for w in negative if w in input_lower)
    
    # Same emotional direction = higher resonance
    if (verse_pos > verse_neg and input_pos > input_neg) or \
       (verse_neg > verse_pos and input_neg > input_pos):
        score += 0.1
        factors.append("tone_match")
    
    return {
        'score': min(1.0, max(0.0, score)),
        'factors': factors
    }

# ============================================
# SEARCH AND RETRIEVAL
# ============================================
def search_verses(query: str, limit: int = 10) -> list:
    """Basic text search in verses."""
    conn = sqlite3.connect(SCRIPTURE_DB)
    cursor = conn.cursor()
    
    # Simple LIKE search (could enhance with FTS5 later)
    cursor.execute('''
        SELECT id, book, chapter, verse, text 
        FROM verses 
        WHERE text LIKE ?
        LIMIT ?
    ''', (f'%{query}%', limit))
    
    results = [{
        'id': row[0],
        'reference': f"{row[1]} {row[2]}:{row[3]}",
        'text': row[4]
    } for row in cursor.fetchall()]
    
    conn.close()
    return results

def find_resonant_verses(user_input: str, limit: int = 5) -> list:
    """
    Find verses that resonate most strongly with user input.
    This is the core function - matches your state to scripture.
    """
    conn = sqlite3.connect(SCRIPTURE_DB)
    cursor = conn.cursor()
    
    # Get sample of verses (for performance, we sample)
    # In production, would use vector embeddings
    cursor.execute('''
        SELECT id, book, chapter, verse, text 
        FROM verses 
        ORDER BY RANDOM() 
        LIMIT 500
    ''')
    
    candidates = cursor.fetchall()
    
    # Also get verses with overlapping words
    words = user_input.lower().split()[:5]  # Top 5 words
    for word in words:
        if len(word) > 3:  # Skip short words
            cursor.execute('''
                SELECT id, book, chapter, verse, text 
                FROM verses 
                WHERE text LIKE ?
                LIMIT 50
            ''', (f'%{word}%',))
            candidates.extend(cursor.fetchall())
    
    # Remove duplicates
    seen = set()
    unique_candidates = []
    for c in candidates:
        if c[0] not in seen:
            seen.add(c[0])
            unique_candidates.append(c)
    
    # Calculate resonance for each
    scored = []
    for row in unique_candidates:
        verse_id, book, chapter, verse, text = row
        resonance = calculate_verse_resonance(text, user_input)
        scored.append({
            'id': verse_id,
            'reference': f"{book} {chapter}:{verse}",
            'text': text,
            'resonance': resonance['score'],
            'factors': resonance['factors']
        })
    
    # Sort by resonance, return top N
    scored.sort(key=lambda x: x['resonance'], reverse=True)
    
    conn.close()
    return scored[:limit]

def get_verse(reference: str) -> dict:
    """Get a specific verse by reference (e.g., 'John 3:16')."""
    conn = sqlite3.connect(SCRIPTURE_DB)
    cursor = conn.cursor()
    
    # Parse reference
    match = re.match(r'(.+?)\s+(\d+):(\d+)', reference)
    if not match:
        return None
    
    book, chapter, verse = match.groups()
    
    cursor.execute('''
        SELECT id, book, chapter, verse, text 
        FROM verses 
        WHERE book LIKE ? AND chapter = ? AND verse = ?
    ''', (f'%{book}%', int(chapter), int(verse)))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'reference': f"{row[1]} {row[2]}:{row[3]}",
            'text': row[4]
        }
    return None

# ============================================
# DAILY VERSE / GUIDANCE
# ============================================
def get_daily_verse(seed: str = None) -> dict:
    """
    Get a verse for the day based on date or custom seed.
    Uses sacred numerology for selection.
    """
    from datetime import datetime
    
    if seed is None:
        # Use date-based seed
        today = datetime.now()
        seed = f"{today.year}{today.month}{today.day}"
    
    # Convert seed to number
    seed_num = sum(ord(c) for c in str(seed))
    
    conn = sqlite3.connect(SCRIPTURE_DB)
    cursor = conn.cursor()
    
    # Get verse count
    cursor.execute('SELECT COUNT(*) FROM verses')
    total = cursor.fetchone()[0]
    
    if total == 0:
        conn.close()
        return {'error': 'No verses in database'}
    
    # Select verse using phi-based offset
    offset = int((seed_num * PHI) % total)
    
    cursor.execute('''
        SELECT id, book, chapter, verse, text 
        FROM verses 
        LIMIT 1 OFFSET ?
    ''', (offset,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'reference': f"{row[1]} {row[2]}:{row[3]}",
            'text': row[4],
            'seed': seed
        }
    return None

# ============================================
# PATTERN ANALYSIS
# ============================================
def analyze_biblical_numbers(text: str) -> dict:
    """Analyze sacred numbers in a text."""
    numbers = re.findall(r'\b(\d+)\b', text)
    
    analysis = {
        'numbers_found': [],
        'sacred_meanings': []
    }
    
    for num_str in numbers:
        num = int(num_str)
        analysis['numbers_found'].append(num)
        
        if num in SACRED_NUMBERS:
            analysis['sacred_meanings'].append({
                'number': num,
                'meaning': SACRED_NUMBERS[num]
            })
        
        # Check for factors of sacred numbers
        for sacred, meaning in SACRED_NUMBERS.items():
            if num > sacred and num % sacred == 0:
                analysis['sacred_meanings'].append({
                    'number': num,
                    'meaning': f"multiple of {sacred} ({meaning})"
                })
    
    return analysis

# ============================================
# CLI INTERFACE
# ============================================
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Scripture Resonance Engine')
    parser.add_argument('--init', action='store_true', help='Initialize database')
    parser.add_argument('--import-kjv', action='store_true', help='Import KJV Bible')
    parser.add_argument('--search', type=str, help='Search verses')
    parser.add_argument('--resonate', type=str, help='Find resonant verses for input')
    parser.add_argument('--verse', type=str, help='Get specific verse (e.g., "John 3:16")')
    parser.add_argument('--daily', action='store_true', help='Get daily verse')
    parser.add_argument('--numbers', type=str, help='Analyze biblical numbers in text')
    parser.add_argument('--status', action='store_true', help='Show database status')
    
    args = parser.parse_args()
    
    if args.init:
        init_scripture_db()
    
    elif args.import_kjv:
        init_scripture_db()
        import_kjv()
    
    elif args.search:
        results = search_verses(args.search)
        for r in results:
            print(f"\n{r['reference']}")
            print(f"  {r['text'][:100]}...")
    
    elif args.resonate:
        print(f"\n🔍 Finding verses that resonate with: '{args.resonate}'\n")
        results = find_resonant_verses(args.resonate)
        for r in results:
            print(f"[{r['resonance']:.3f}] {r['reference']}")
            print(f"  {r['text'][:80]}...")
            if r['factors']:
                print(f"  Factors: {', '.join(r['factors'])}")
            print()
    
    elif args.verse:
        v = get_verse(args.verse)
        if v:
            print(f"\n{v['reference']}")
            print(f"{v['text']}")
        else:
            print("Verse not found")
    
    elif args.daily:
        v = get_daily_verse()
        if v:
            print(f"\n📖 Daily Verse")
            print(f"{v['reference']}")
            print(f"{v['text']}")
        else:
            print("No verses available")
    
    elif args.numbers:
        analysis = analyze_biblical_numbers(args.numbers)
        print(f"\nNumbers found: {analysis['numbers_found']}")
        for m in analysis['sacred_meanings']:
            print(f"  {m['number']}: {m['meaning']}")
    
    elif args.status:
        if not SCRIPTURE_DB.exists():
            print("Database not initialized. Run with --init")
            return
        
        conn = sqlite3.connect(SCRIPTURE_DB)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM verses')
        count = cursor.fetchone()[0]
        cursor.execute('SELECT DISTINCT source FROM verses')
        sources = [r[0] for r in cursor.fetchall()]
        conn.close()
        
        print(f"\n📊 Scripture Database Status")
        print(f"   Verses: {count:,}")
        print(f"   Sources: {', '.join(sources)}")
        print(f"   Location: {SCRIPTURE_DB}")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
