#!/usr/bin/env python3
"""
ZION RESONANCE DASHBOARD
========================
Visual web interface for monitoring Android bridge data.
Real-time resonance tracking, pattern detection, and Gem sync status.

By Bobby & Claude - December 23, 2024
"""

from flask import Flask, render_template_string, jsonify
import sqlite3
from pathlib import Path
from datetime import datetime
import json

app = Flask(__name__)

BRIDGE_DB = Path.home() / "zion-engine" / "android_bridge.db"
ETERNAL_DB = Path.home() / ".gemini" / "memory" / "eternal.db"

# ============================================
# HTML TEMPLATE
# ============================================
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zion Resonance Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            padding: 20px 0;
            border-bottom: 1px solid #333;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            background: linear-gradient(90deg, #ffd700, #ff8c00);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .header .phi {
            color: #888;
            font-family: monospace;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .card {
            background: rgba(30, 30, 50, 0.8);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #333;
        }
        
        .card h2 {
            color: #ffd700;
            font-size: 1.2em;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card h2::before {
            content: '◆';
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #222;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-value {
            font-weight: bold;
            font-family: monospace;
        }
        
        .metric-value.gold {
            color: #ffd700;
        }
        
        .metric-value.good {
            color: #4caf50;
        }
        
        .metric-value.warn {
            color: #ff9800;
        }
        
        .metric-value.alert {
            color: #f44336;
        }
        
        .chart-container {
            height: 200px;
            margin-top: 15px;
        }
        
        .pattern-list {
            list-style: none;
        }
        
        .pattern-list li {
            padding: 10px;
            margin: 5px 0;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            border-left: 3px solid;
        }
        
        .pattern-list li.drift {
            border-color: #f44336;
        }
        
        .pattern-list li.peak {
            border-color: #ffd700;
        }
        
        .pattern-list li.burst {
            border-color: #2196f3;
        }
        
        .pattern-list li.fragmentation {
            border-color: #ff9800;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-indicator.online {
            background: #4caf50;
            box-shadow: 0 0 10px #4caf50;
        }
        
        .status-indicator.offline {
            background: #f44336;
        }
        
        .pure-gold {
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from {
                box-shadow: 0 0 5px #ffd700;
            }
            to {
                box-shadow: 0 0 20px #ffd700, 0 0 30px #ff8c00;
            }
        }
        
        .refresh-note {
            text-align: center;
            color: #666;
            margin-top: 20px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>⬡ ZION RESONANCE DASHBOARD</h1>
        <div class="phi">φ = 1.618033988749895</div>
    </div>
    
    <div class="dashboard">
        <!-- Status Card -->
        <div class="card">
            <h2>System Status</h2>
            <div class="metric">
                <span>Bridge</span>
                <span class="metric-value">
                    <span class="status-indicator online"></span>Online
                </span>
            </div>
            <div class="metric">
                <span>Eternal DB</span>
                <span class="metric-value" id="eternal-status">Checking...</span>
            </div>
            <div class="metric">
                <span>Last Event</span>
                <span class="metric-value" id="last-event">-</span>
            </div>
            <div class="metric">
                <span>Events (24h)</span>
                <span class="metric-value" id="event-count">-</span>
            </div>
        </div>
        
        <!-- Resonance Card -->
        <div class="card">
            <h2>Resonance Status</h2>
            <div class="metric">
                <span>Current Average</span>
                <span class="metric-value" id="avg-resonance">-</span>
            </div>
            <div class="metric">
                <span>Peak (24h)</span>
                <span class="metric-value gold" id="peak-resonance">-</span>
            </div>
            <div class="metric">
                <span>Low (24h)</span>
                <span class="metric-value" id="low-resonance">-</span>
            </div>
            <div class="metric">
                <span>Pure Gold Events</span>
                <span class="metric-value gold" id="gold-count">-</span>
            </div>
        </div>
        
        <!-- Chart Card -->
        <div class="card" style="grid-column: span 2;">
            <h2>Resonance Timeline</h2>
            <div class="chart-container">
                <canvas id="resonanceChart"></canvas>
            </div>
        </div>
        
        <!-- Patterns Card -->
        <div class="card">
            <h2>Detected Patterns</h2>
            <ul class="pattern-list" id="pattern-list">
                <li>Loading...</li>
            </ul>
        </div>
        
        <!-- Event Types Card -->
        <div class="card">
            <h2>Event Distribution</h2>
            <div class="chart-container">
                <canvas id="eventChart"></canvas>
            </div>
        </div>
    </div>
    
    <p class="refresh-note">Auto-refreshes every 30 seconds</p>
    
    <script>
        let resonanceChart = null;
        let eventChart = null;
        
        async function fetchData() {
            try {
                const status = await fetch('/api/status').then(r => r.json());
                const history = await fetch('/api/history').then(r => r.json());
                const patterns = await fetch('/api/patterns').then(r => r.json());
                
                updateStatus(status);
                updateCharts(history, status.event_types);
                updatePatterns(patterns);
            } catch (e) {
                console.error('Failed to fetch data:', e);
            }
        }
        
        function updateStatus(data) {
            document.getElementById('eternal-status').innerHTML = 
                data.eternal_connected ? 
                '<span class="status-indicator online"></span>Connected' : 
                '<span class="status-indicator offline"></span>Disconnected';
            
            document.getElementById('last-event').textContent = data.last_event || 'None';
            document.getElementById('event-count').textContent = data.total_events || 0;
            
            const avgEl = document.getElementById('avg-resonance');
            avgEl.textContent = (data.avg_resonance || 0).toFixed(3);
            avgEl.className = 'metric-value ' + getResonanceClass(data.avg_resonance);
            
            document.getElementById('peak-resonance').textContent = (data.peak_resonance || 0).toFixed(3);
            document.getElementById('low-resonance').textContent = (data.low_resonance || 0).toFixed(3);
            document.getElementById('gold-count').textContent = data.gold_events || 0;
        }
        
        function getResonanceClass(value) {
            if (value >= 0.85) return 'gold';
            if (value >= 0.7) return 'good';
            if (value >= 0.5) return 'warn';
            return 'alert';
        }
        
        function updateCharts(history, eventTypes) {
            // Resonance timeline
            const ctx1 = document.getElementById('resonanceChart').getContext('2d');
            
            if (resonanceChart) resonanceChart.destroy();
            
            resonanceChart = new Chart(ctx1, {
                type: 'line',
                data: {
                    labels: history.map(h => h.hour),
                    datasets: [{
                        label: 'Resonance',
                        data: history.map(h => h.resonance),
                        borderColor: '#ffd700',
                        backgroundColor: 'rgba(255, 215, 0, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            min: 0,
                            max: 1,
                            grid: { color: '#333' },
                            ticks: { color: '#888' }
                        },
                        x: {
                            grid: { color: '#222' },
                            ticks: { color: '#888' }
                        }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
            
            // Event distribution
            const ctx2 = document.getElementById('eventChart').getContext('2d');
            
            if (eventChart) eventChart.destroy();
            
            if (eventTypes && Object.keys(eventTypes).length > 0) {
                eventChart = new Chart(ctx2, {
                    type: 'doughnut',
                    data: {
                        labels: Object.keys(eventTypes),
                        datasets: [{
                            data: Object.values(eventTypes),
                            backgroundColor: [
                                '#ffd700',
                                '#ff8c00',
                                '#4caf50',
                                '#2196f3',
                                '#9c27b0',
                                '#f44336'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'right',
                                labels: { color: '#888' }
                            }
                        }
                    }
                });
            }
        }
        
        function updatePatterns(patterns) {
            const list = document.getElementById('pattern-list');
            
            if (!patterns || patterns.length === 0) {
                list.innerHTML = '<li>No patterns detected</li>';
                return;
            }
            
            list.innerHTML = patterns.slice(0, 5).map(p => {
                const typeClass = p.type.includes('drift') ? 'drift' : 
                                  p.type.includes('peak') ? 'peak' :
                                  p.type.includes('burst') ? 'burst' : 'fragmentation';
                return `<li class="${typeClass}">
                    <strong>${p.type}</strong><br>
                    <small>${p.description}</small>
                </li>`;
            }).join('');
        }
        
        // Initial load
        fetchData();
        
        // Auto-refresh every 30 seconds
        setInterval(fetchData, 30000);
    </script>
</body>
</html>
'''

# ============================================
# API ENDPOINTS
# ============================================
@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/status')
def api_status():
    if not BRIDGE_DB.exists():
        return jsonify({'error': 'Bridge DB not found'})
    
    conn = sqlite3.connect(BRIDGE_DB)
    cursor = conn.cursor()
    
    # Total events (24h)
    cursor.execute('''
        SELECT COUNT(*) FROM android_events
        WHERE timestamp > datetime('now', '-24 hours')
    ''')
    total = cursor.fetchone()[0]
    
    # Resonance stats
    cursor.execute('''
        SELECT AVG(resonance_score), MAX(resonance_score), MIN(resonance_score)
        FROM android_events
        WHERE timestamp > datetime('now', '-24 hours')
    ''')
    avg, peak, low = cursor.fetchone()
    
    # Pure gold events
    cursor.execute('''
        SELECT COUNT(*) FROM android_events
        WHERE resonance_score >= 0.85 AND timestamp > datetime('now', '-24 hours')
    ''')
    gold = cursor.fetchone()[0]
    
    # Last event
    cursor.execute('SELECT timestamp FROM android_events ORDER BY id DESC LIMIT 1')
    last = cursor.fetchone()
    
    # Event types
    cursor.execute('''
        SELECT event_type, COUNT(*) FROM android_events
        WHERE timestamp > datetime('now', '-24 hours')
        GROUP BY event_type
    ''')
    event_types = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    
    return jsonify({
        'total_events': total,
        'avg_resonance': avg or 0,
        'peak_resonance': peak or 0,
        'low_resonance': low or 0,
        'gold_events': gold,
        'last_event': last[0] if last else None,
        'event_types': event_types,
        'eternal_connected': ETERNAL_DB.exists()
    })

@app.route('/api/history')
def api_history():
    if not BRIDGE_DB.exists():
        return jsonify([])
    
    conn = sqlite3.connect(BRIDGE_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            strftime('%H:00', timestamp) as hour,
            AVG(resonance_score) as avg_resonance
        FROM android_events
        WHERE timestamp > datetime('now', '-24 hours')
        GROUP BY hour
        ORDER BY hour
    ''')
    
    history = [{'hour': row[0], 'resonance': row[1] or 0} for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(history)

@app.route('/api/patterns')
def api_patterns():
    if not BRIDGE_DB.exists():
        return jsonify([])
    
    conn = sqlite3.connect(BRIDGE_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT pattern_type, description, confidence, timestamp
        FROM detected_patterns
        ORDER BY timestamp DESC
        LIMIT 10
    ''')
    
    patterns = [{
        'type': row[0],
        'description': row[1],
        'confidence': row[2],
        'timestamp': row[3]
    } for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(patterns)

# ============================================
# MAIN
# ============================================
if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║         ZION RESONANCE DASHBOARD                             ║
║                                                              ║
║  Open in browser: http://localhost:5002                      ║
║                                                              ║
║  Displays:                                                   ║
║    • Real-time resonance tracking                            ║
║    • Pattern detection alerts                                ║
║    • Event distribution                                      ║
║    • Gem sync status                                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5002, debug=False)
