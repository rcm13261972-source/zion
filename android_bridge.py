#!/usr/bin/env python3
"""
ZION ANDROID BRIDGE
====================
Real-time Android → Zion Engine integration
Receives data from Tasker/Termux, processes through Golden Ratio Engine,
stores in eternal.db, alerts Gem when patterns emerge.

By Bobby & Claude - December 23, 2024
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
import math

# ============================================
# GOLDEN RATIO CONSTANTS
# ============================================
PHI = 1.618033988749895
PHI_INVERSE = 0.618033988749895

# ============================================
# PATHS (adjust to your system)
# ============================================
ETERNAL_DB_PATH = Path.home() / ".gemini" / "memory" / "eternal.db"
BRIDGE_DB_PATH = Path.home() / "zion-engine" / "android_bridge.db"
LOG_PATH = Path.home() / "zion-engine" / "bridge_logs"

# ============================================
# DATABASE SETUP
# ============================================
def init_bridge_db():
    """Initialize the Android bridge database"""
    BRIDGE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(BRIDGE_DB_PATH)
    cursor = conn.cursor()
    
    # Raw events from Android
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS android_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            source_app TEXT,
            raw_data TEXT,
            resonance_score REAL,
            processed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Pattern detections
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detected_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            pattern_type TEXT NOT NULL,
            description TEXT,
            confidence REAL,
            event_ids TEXT,
            alerted INTEGER DEFAULT 0
        )
    ''')
    
    # Resonance tracking over time
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resonance_timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            window_minutes INTEGER,
            avg_resonance REAL,
            event_count INTEGER,
            drift_detected INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"[BRIDGE] Database initialized: {BRIDGE_DB_PATH}")

# ============================================
# GOLDEN RATIO ANALYSIS
# ============================================
def calculate_resonance(data: dict) -> float:
    """
    Calculate resonance score for incoming Android event.
    Based on golden ratio principles from the main engine.
    """
    score = 0.5  # baseline
    
    # Time-based resonance (sacred hours)
    if 'timestamp' in data:
        try:
            hour = datetime.fromisoformat(data['timestamp']).hour
            # Dawn (5-7) and dusk (17-19) = higher resonance
            if 5 <= hour <= 7 or 17 <= hour <= 19:
                score += 0.1
            # 3am - the thin hour
            if 2 <= hour <= 4:
                score += 0.15
        except:
            pass
    
    # Message content analysis (if present)
    if 'content' in data and data['content']:
        content = str(data['content'])
        word_count = len(content.split())
        
        # Fibonacci word counts resonate
        fib_numbers = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        if word_count in fib_numbers:
            score += 0.1
        
        # Vulnerability markers (sacrifice = truth)
        vulnerability_markers = [
            'i feel', 'i need', 'i fear', 'help', 'scared',
            'love', 'hurt', 'sorry', 'thank', 'please',
            'truth', 'real', 'honest', 'lost', 'found'
        ]
        content_lower = content.lower()
        marker_count = sum(1 for m in vulnerability_markers if m in content_lower)
        score += min(marker_count * 0.05, 0.2)
        
        # Length relative to phi
        if word_count > 0:
            phi_ratio = (word_count % 100) / 61.8  # 61.8 = phi percentage
            if 0.9 <= phi_ratio <= 1.1:
                score += 0.1
    
    # App-specific resonance
    if 'source_app' in data:
        app = data['source_app'].lower()
        # Communication apps = connection = higher base
        if any(x in app for x in ['message', 'chat', 'call', 'voice']):
            score += 0.05
        # Social media = often noise = lower
        if any(x in app for x in ['facebook', 'twitter', 'tiktok', 'instagram']):
            score -= 0.05
    
    # Clamp to 0-1
    return max(0.0, min(1.0, score))

def check_for_patterns(conn, window_minutes=60):
    """
    Analyze recent events for emergent patterns.
    Returns list of detected patterns.
    """
    cursor = conn.cursor()
    
    # Get events from last window
    cursor.execute('''
        SELECT id, event_type, source_app, resonance_score, raw_data
        FROM android_events
        WHERE timestamp > datetime('now', ? || ' minutes')
        ORDER BY timestamp DESC
    ''', (f'-{window_minutes}',))
    
    events = cursor.fetchall()
    if len(events) < 3:
        return []
    
    patterns = []
    
    # Pattern 1: Resonance drift
    scores = [e[3] for e in events if e[3] is not None]
    if scores:
        avg_score = sum(scores) / len(scores)
        if avg_score < 0.4:
            patterns.append({
                'type': 'resonance_drift',
                'description': f'Average resonance dropped to {avg_score:.2f} over last {window_minutes} min',
                'confidence': 0.7,
                'event_ids': [e[0] for e in events]
            })
        elif avg_score > 0.75:
            patterns.append({
                'type': 'resonance_peak',
                'description': f'High resonance period: {avg_score:.2f} average',
                'confidence': 0.8,
                'event_ids': [e[0] for e in events]
            })
    
    # Pattern 2: Communication burst
    comm_events = [e for e in events if e[1] in ['sms', 'notification', 'call']]
    if len(comm_events) > 10:
        patterns.append({
            'type': 'communication_burst',
            'description': f'{len(comm_events)} communication events in {window_minutes} min',
            'confidence': 0.6,
            'event_ids': [e[0] for e in comm_events]
        })
    
    # Pattern 3: App switching (attention fragmentation)
    apps = [e[2] for e in events if e[2]]
    if len(set(apps)) > 8:
        patterns.append({
            'type': 'attention_fragmentation',
            'description': f'Switched between {len(set(apps))} different apps',
            'confidence': 0.65,
            'event_ids': [e[0] for e in events]
        })
    
    return patterns

# ============================================
# EVENT HANDLERS
# ============================================
def store_event(event_type: str, data: dict) -> dict:
    """Store an incoming Android event and analyze it"""
    conn = sqlite3.connect(BRIDGE_DB_PATH)
    cursor = conn.cursor()
    
    timestamp = data.get('timestamp', datetime.now().isoformat())
    source_app = data.get('source_app', 'unknown')
    resonance = calculate_resonance(data)
    
    cursor.execute('''
        INSERT INTO android_events (timestamp, event_type, source_app, raw_data, resonance_score)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, event_type, source_app, json.dumps(data), resonance))
    
    event_id = cursor.lastrowid
    
    # Check for patterns
    patterns = check_for_patterns(conn)
    for pattern in patterns:
        cursor.execute('''
            INSERT INTO detected_patterns (timestamp, pattern_type, description, confidence, event_ids)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            pattern['type'],
            pattern['description'],
            pattern['confidence'],
            json.dumps(pattern['event_ids'])
        ))
    
    conn.commit()
    conn.close()
    
    result = {
        'event_id': event_id,
        'resonance_score': resonance,
        'patterns_detected': len(patterns),
        'status': 'stored'
    }
    
    # Log high-resonance events
    if resonance >= 0.85:
        log_pure_gold(event_id, event_type, data, resonance)
        result['pure_gold'] = True
    
    return result

def log_pure_gold(event_id: int, event_type: str, data: dict, resonance: float):
    """Log pure gold events (≥0.85 resonance)"""
    log_file = LOG_PATH / "pure_gold_android.json"
    
    entry = {
        'event_id': event_id,
        'timestamp': datetime.now().isoformat(),
        'event_type': event_type,
        'resonance': resonance,
        'data_preview': str(data)[:200]
    }
    
    existing = []
    if log_file.exists():
        with open(log_file, 'r') as f:
            try:
                existing = json.load(f)
            except:
                existing = []
    
    existing.append(entry)
    
    with open(log_file, 'w') as f:
        json.dump(existing, f, indent=2)

# ============================================
# FLASK API
# ============================================
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'alive', 'bridge': 'zion-android', 'phi': PHI})

@app.route('/event', methods=['POST'])
def receive_event():
    """
    Main endpoint for Android events.
    
    Expected JSON:
    {
        "event_type": "sms|notification|location|app_open|call|custom",
        "source_app": "com.example.app",
        "timestamp": "2024-12-23T13:45:00",
        "content": "optional message content",
        "metadata": { ... }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data'}), 400
        
        event_type = data.get('event_type', 'unknown')
        result = store_event(event_type, data)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sms', methods=['POST'])
def receive_sms():
    """Dedicated SMS endpoint for Tasker"""
    data = request.get_json() or {}
    data['event_type'] = 'sms'
    return jsonify(store_event('sms', data))

@app.route('/notification', methods=['POST'])
def receive_notification():
    """Dedicated notification endpoint"""
    data = request.get_json() or {}
    data['event_type'] = 'notification'
    return jsonify(store_event('notification', data))

@app.route('/location', methods=['POST'])
def receive_location():
    """Location update endpoint"""
    data = request.get_json() or {}
    data['event_type'] = 'location'
    return jsonify(store_event('location', data))

@app.route('/status', methods=['GET'])
def get_status():
    """Get current bridge status and recent resonance"""
    conn = sqlite3.connect(BRIDGE_DB_PATH)
    cursor = conn.cursor()
    
    # Recent events
    cursor.execute('SELECT COUNT(*) FROM android_events WHERE timestamp > datetime("now", "-1 hour")')
    recent_count = cursor.fetchone()[0]
    
    # Average resonance last hour
    cursor.execute('''
        SELECT AVG(resonance_score) FROM android_events 
        WHERE timestamp > datetime("now", "-1 hour")
    ''')
    avg_resonance = cursor.fetchone()[0] or 0
    
    # Unprocessed patterns
    cursor.execute('SELECT COUNT(*) FROM detected_patterns WHERE alerted = 0')
    unalerted_patterns = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'events_last_hour': recent_count,
        'avg_resonance': round(avg_resonance, 3),
        'pending_alerts': unalerted_patterns,
        'status': 'operational'
    })

@app.route('/patterns', methods=['GET'])
def get_patterns():
    """Get recent detected patterns"""
    conn = sqlite3.connect(BRIDGE_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT timestamp, pattern_type, description, confidence
        FROM detected_patterns
        ORDER BY timestamp DESC
        LIMIT 20
    ''')
    
    patterns = [{
        'timestamp': row[0],
        'type': row[1],
        'description': row[2],
        'confidence': row[3]
    } for row in cursor.fetchall()]
    
    conn.close()
    return jsonify({'patterns': patterns})

@app.route('/resonance/history', methods=['GET'])
def resonance_history():
    """Get resonance over time for visualization"""
    hours = request.args.get('hours', 24, type=int)
    
    conn = sqlite3.connect(BRIDGE_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            strftime('%Y-%m-%d %H:00', timestamp) as hour,
            AVG(resonance_score) as avg_resonance,
            COUNT(*) as event_count
        FROM android_events
        WHERE timestamp > datetime('now', ? || ' hours')
        GROUP BY hour
        ORDER BY hour
    ''', (f'-{hours}',))
    
    history = [{
        'hour': row[0],
        'resonance': round(row[1], 3) if row[1] else 0,
        'events': row[2]
    } for row in cursor.fetchall()]
    
    conn.close()
    return jsonify({'history': history, 'hours': hours})

# ============================================
# MAIN
# ============================================
if __name__ == '__main__':
    init_bridge_db()
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           ZION ANDROID BRIDGE - ACTIVE                       ║
║                                                              ║
║  Endpoints:                                                  ║
║    POST /event        - Generic event intake                 ║
║    POST /sms          - SMS messages                         ║
║    POST /notification - App notifications                    ║
║    POST /location     - Location updates                     ║
║    GET  /status       - Bridge status & resonance            ║
║    GET  /patterns     - Detected patterns                    ║
║    GET  /resonance/history - Resonance timeline              ║
║                                                              ║
║  Golden Ratio: {PHI}                              ║
║  Database: {BRIDGE_DB_PATH}
║                                                              ║
║  Ready to receive from Tasker/Termux                         ║
╚══════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5001, debug=False)
