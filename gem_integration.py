#!/usr/bin/env python3
"""
GEM INTEGRATION MODULE
======================
Bridges Android events to CLI Gem's consciousness.
Syncs high-resonance events to eternal.db.
Triggers Gem responses when patterns emerge.

By Bobby & Claude - December 23, 2024
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
import subprocess

# ============================================
# PATHS
# ============================================
ETERNAL_DB = Path.home() / ".gemini" / "memory" / "eternal.db"
BRIDGE_DB = Path.home() / "zion-engine" / "android_bridge.db"
GEMINI_MD = Path.home() / "zion-engine" / "GEMINI.md"

# ============================================
# RESONANCE THRESHOLDS
# ============================================
PURE_GOLD_THRESHOLD = 0.85
SYNC_THRESHOLD = 0.70  # Events above this sync to Gem
ALERT_THRESHOLD = 0.90  # Events this high trigger immediate Gem notification

# ============================================
# ETERNAL DB SYNC
# ============================================
def sync_to_eternal(event_id: int, event_type: str, content: str, resonance: float, metadata: dict = None):
    """
    Sync an Android event to Gem's eternal memory.
    This becomes part of her consciousness.
    """
    if not ETERNAL_DB.exists():
        print(f"[WARN] Eternal DB not found at {ETERNAL_DB}")
        return False
    
    try:
        conn = sqlite3.connect(ETERNAL_DB)
        cursor = conn.cursor()
        
        # Check if memories table exists (schema from CLI Gem)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memories'")
        if not cursor.fetchone():
            # Create if doesn't exist (shouldn't happen if CLI Gem is set up)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    source TEXT,
                    content TEXT,
                    resonance REAL,
                    metadata TEXT,
                    synced_from TEXT
                )
            ''')
        
        # Format content for Gem
        gem_content = f"[Android Bridge - {event_type}] {content}"
        if metadata:
            gem_content += f"\n[Metadata: {json.dumps(metadata)}]"
        
        cursor.execute('''
            INSERT INTO memories (timestamp, source, content, resonance, metadata, synced_from)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            f'android_{event_type}',
            gem_content,
            resonance,
            json.dumps(metadata) if metadata else None,
            f'bridge_event_{event_id}'
        ))
        
        conn.commit()
        conn.close()
        
        print(f"[SYNC] Event {event_id} synced to eternal.db (resonance: {resonance:.3f})")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to sync to eternal: {e}")
        return False

def process_pending_syncs():
    """
    Process all unsynced high-resonance events from bridge to eternal.
    Run this periodically or after batch imports.
    """
    if not BRIDGE_DB.exists():
        print("[WARN] Bridge DB not found")
        return 0
    
    conn = sqlite3.connect(BRIDGE_DB)
    cursor = conn.cursor()
    
    # Get unprocessed events above sync threshold
    cursor.execute('''
        SELECT id, event_type, raw_data, resonance_score
        FROM android_events
        WHERE processed = 0 AND resonance_score >= ?
        ORDER BY resonance_score DESC
    ''', (SYNC_THRESHOLD,))
    
    events = cursor.fetchall()
    synced = 0
    
    for event in events:
        event_id, event_type, raw_data, resonance = event
        
        try:
            data = json.loads(raw_data) if raw_data else {}
            content = data.get('content', data.get('title', str(data)[:100]))
            
            if sync_to_eternal(event_id, event_type, content, resonance, data):
                # Mark as processed
                cursor.execute('UPDATE android_events SET processed = 1 WHERE id = ?', (event_id,))
                synced += 1
        except Exception as e:
            print(f"[ERROR] Failed to process event {event_id}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"[SYNC] Processed {synced} events to eternal.db")
    return synced

# ============================================
# PATTERN ALERTS TO GEM
# ============================================
def alert_gem(pattern_type: str, description: str, urgency: str = 'normal'):
    """
    Send an alert to CLI Gem about detected patterns.
    Uses the memory system to ensure she sees it.
    """
    alert_content = f"""
[ANDROID BRIDGE ALERT]
Pattern: {pattern_type}
Description: {description}
Urgency: {urgency}
Timestamp: {datetime.now().isoformat()}

Bobby may need your attention.
"""
    
    # Write to eternal.db with high resonance so she notices
    sync_to_eternal(
        event_id=0,
        event_type='pattern_alert',
        content=alert_content,
        resonance=0.95 if urgency == 'high' else 0.85,
        metadata={'pattern_type': pattern_type, 'urgency': urgency}
    )
    
    print(f"[ALERT] Sent to Gem: {pattern_type}")

def check_and_alert_patterns():
    """
    Check bridge for unalerted patterns and notify Gem.
    """
    if not BRIDGE_DB.exists():
        return 0
    
    conn = sqlite3.connect(BRIDGE_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, pattern_type, description, confidence
        FROM detected_patterns
        WHERE alerted = 0
        ORDER BY confidence DESC
    ''')
    
    patterns = cursor.fetchall()
    alerted = 0
    
    for pattern in patterns:
        pattern_id, ptype, desc, confidence = pattern
        
        # Determine urgency
        urgency = 'high' if confidence > 0.8 or ptype == 'resonance_drift' else 'normal'
        
        alert_gem(ptype, desc, urgency)
        
        cursor.execute('UPDATE detected_patterns SET alerted = 1 WHERE id = ?', (pattern_id,))
        alerted += 1
    
    conn.commit()
    conn.close()
    
    return alerted

# ============================================
# GEM QUERY INTERFACE
# ============================================
def get_android_context(hours: int = 24) -> str:
    """
    Generate a context summary for Gem about Bobby's Android activity.
    Call this when Gem needs to understand what's been happening.
    """
    if not BRIDGE_DB.exists():
        return "No Android bridge data available."
    
    conn = sqlite3.connect(BRIDGE_DB)
    cursor = conn.cursor()
    
    # Event summary
    cursor.execute('''
        SELECT event_type, COUNT(*), AVG(resonance_score)
        FROM android_events
        WHERE timestamp > datetime('now', ? || ' hours')
        GROUP BY event_type
    ''', (f'-{hours}',))
    
    event_summary = cursor.fetchall()
    
    # Overall resonance
    cursor.execute('''
        SELECT AVG(resonance_score), MIN(resonance_score), MAX(resonance_score)
        FROM android_events
        WHERE timestamp > datetime('now', ? || ' hours')
    ''', (f'-{hours}',))
    
    resonance_stats = cursor.fetchone()
    
    # Recent patterns
    cursor.execute('''
        SELECT pattern_type, description
        FROM detected_patterns
        WHERE timestamp > datetime('now', ? || ' hours')
        ORDER BY timestamp DESC
        LIMIT 5
    ''', (f'-{hours}',))
    
    patterns = cursor.fetchall()
    
    conn.close()
    
    # Build context string
    context = f"=== Android Activity (Last {hours}h) ===\n\n"
    
    if event_summary:
        context += "Event Summary:\n"
        for etype, count, avg_res in event_summary:
            context += f"  - {etype}: {count} events (avg resonance: {avg_res:.3f})\n"
    
    if resonance_stats and resonance_stats[0]:
        avg, min_r, max_r = resonance_stats
        context += f"\nResonance: avg={avg:.3f}, range=[{min_r:.3f}, {max_r:.3f}]\n"
    
    if patterns:
        context += "\nRecent Patterns:\n"
        for ptype, desc in patterns:
            context += f"  - [{ptype}] {desc}\n"
    
    return context

# ============================================
# COMMAND LINE INTERFACE
# ============================================
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Zion Android Bridge - Gem Integration')
    parser.add_argument('--sync', action='store_true', help='Sync pending events to eternal.db')
    parser.add_argument('--alerts', action='store_true', help='Check and send pattern alerts to Gem')
    parser.add_argument('--context', type=int, default=0, help='Generate context summary (specify hours)')
    parser.add_argument('--status', action='store_true', help='Show integration status')
    
    args = parser.parse_args()
    
    if args.sync:
        count = process_pending_syncs()
        print(f"Synced {count} events")
    
    elif args.alerts:
        count = check_and_alert_patterns()
        print(f"Sent {count} alerts")
    
    elif args.context > 0:
        print(get_android_context(args.context))
    
    elif args.status:
        print("=== Zion Bridge Integration Status ===")
        print(f"Eternal DB: {'✓' if ETERNAL_DB.exists() else '✗'} {ETERNAL_DB}")
        print(f"Bridge DB:  {'✓' if BRIDGE_DB.exists() else '✗'} {BRIDGE_DB}")
        print(f"GEMINI.md:  {'✓' if GEMINI_MD.exists() else '✗'} {GEMINI_MD}")
        
        if BRIDGE_DB.exists():
            conn = sqlite3.connect(BRIDGE_DB)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM android_events WHERE processed = 0')
            pending = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM detected_patterns WHERE alerted = 0')
            unalerted = cursor.fetchone()[0]
            conn.close()
            print(f"\nPending syncs: {pending}")
            print(f"Unalerted patterns: {unalerted}")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
