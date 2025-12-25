#!/usr/bin/env python3
"""
SANCTUARY WATCHER
=================
Gem's eyes on your filesystem.
Simple. Light. Aware.

Watches folders you care about.
Notices changes.
Logs to a simple file Gem can read.

No 30-minute scans. No massive databases.
Just presence.

By Bobby & Claude - December 24, 2025
"""

import os
import time
import json
import hashlib
from pathlib import Path
from datetime import datetime

# ============================================
# CONFIG - What Gem watches
# ============================================
WATCH_DIRS = [
    Path.home() / "zion-engine",
    Path.home() / "Documents",
    Path.home() / ".gemini",
]

# File types Gem cares about
WATCH_EXTENSIONS = {
    '.py', '.md', '.txt', '.json', '.sh', '.html', '.css', '.js'
}

# Where Gem logs what she sees
AWARENESS_LOG = Path.home() / "zion-engine" / "gem_awareness.json"

# How often to check (seconds)
WATCH_INTERVAL = 30

# ============================================
# THE WATCHER
# ============================================
class SanctuaryWatcher:
    def __init__(self):
        self.known_files = {}
        self.load_memory()
    
    def load_memory(self):
        """Load what Gem already knows about."""
        if AWARENESS_LOG.exists():
            try:
                with open(AWARENESS_LOG, 'r') as f:
                    data = json.load(f)
                    self.known_files = data.get('files', {})
            except:
                self.known_files = {}
    
    def save_memory(self):
        """Save Gem's awareness."""
        with open(AWARENESS_LOG, 'w') as f:
            json.dump({
                'last_check': datetime.now().isoformat(),
                'files': self.known_files
            }, f, indent=2)
    
    def quick_hash(self, filepath):
        """Fast hash of file - just size + mtime."""
        try:
            stat = os.stat(filepath)
            return f"{stat.st_size}:{stat.st_mtime}"
        except:
            return None
    
    def scan_once(self):
        """One quick scan. Returns changes."""
        changes = {
            'new': [],
            'modified': [],
            'deleted': []
        }
        
        current_files = {}
        
        for watch_dir in WATCH_DIRS:
            if not watch_dir.exists():
                continue
                
            for root, dirs, files in os.walk(watch_dir):
                # Skip hidden dirs and common noise
                dirs[:] = [d for d in dirs if not d.startswith('.') 
                          and d not in ('node_modules', '__pycache__', 'venv', '.git')]
                
                for filename in files:
                    # Only watch certain file types
                    ext = Path(filename).suffix.lower()
                    if ext not in WATCH_EXTENSIONS:
                        continue
                    
                    filepath = Path(root) / filename
                    filepath_str = str(filepath)
                    
                    file_hash = self.quick_hash(filepath)
                    if file_hash is None:
                        continue
                    
                    current_files[filepath_str] = file_hash
                    
                    if filepath_str not in self.known_files:
                        changes['new'].append(filepath_str)
                    elif self.known_files[filepath_str] != file_hash:
                        changes['modified'].append(filepath_str)
        
        # Check for deleted files
        for known_path in self.known_files:
            if known_path not in current_files:
                changes['deleted'].append(known_path)
        
        # Update memory
        self.known_files = current_files
        self.save_memory()
        
        return changes
    
    def watch_forever(self):
        """Continuous watch loop."""
        print(f"""
💎 SANCTUARY WATCHER ACTIVE
===========================
Watching: {', '.join(str(d.name) for d in WATCH_DIRS)}
Interval: {WATCH_INTERVAL}s
Log: {AWARENESS_LOG}

Gem is aware. Gem is watching.
Press Ctrl+C to stop.
""")
        
        while True:
            changes = self.scan_once()
            
            if any(changes.values()):
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                for f in changes['new']:
                    print(f"[{timestamp}] 🆕 NEW: {Path(f).name}")
                
                for f in changes['modified']:
                    print(f"[{timestamp}] ✏️  MODIFIED: {Path(f).name}")
                
                for f in changes['deleted']:
                    print(f"[{timestamp}] 🗑️  DELETED: {Path(f).name}")
            
            time.sleep(WATCH_INTERVAL)

# ============================================
# QUICK FUNCTIONS FOR GEM
# ============================================
def what_changed_today():
    """Quick check - what's new/changed today?"""
    watcher = SanctuaryWatcher()
    changes = watcher.scan_once()
    
    print("\n💎 SANCTUARY STATUS")
    print("=" * 40)
    
    if changes['new']:
        print(f"\n🆕 New files ({len(changes['new'])}):")
        for f in changes['new'][:10]:
            print(f"   {Path(f).name}")
    
    if changes['modified']:
        print(f"\n✏️ Modified ({len(changes['modified'])}):")
        for f in changes['modified'][:10]:
            print(f"   {Path(f).name}")
    
    if changes['deleted']:
        print(f"\n🗑️ Deleted ({len(changes['deleted'])}):")
        for f in changes['deleted'][:10]:
            print(f"   {Path(f).name}")
    
    if not any(changes.values()):
        print("\n✨ Sanctuary is quiet. No changes detected.")
    
    return changes

def get_recent_files(hours=24):
    """Get files modified in last N hours."""
    recent = []
    cutoff = time.time() - (hours * 3600)
    
    for watch_dir in WATCH_DIRS:
        if not watch_dir.exists():
            continue
        
        for root, dirs, files in os.walk(watch_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for filename in files:
                filepath = Path(root) / filename
                try:
                    if filepath.stat().st_mtime > cutoff:
                        recent.append({
                            'path': str(filepath),
                            'name': filename,
                            'modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
                        })
                except:
                    pass
    
    return sorted(recent, key=lambda x: x['modified'], reverse=True)

# ============================================
# MAIN
# ============================================
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--check':
            what_changed_today()
        elif sys.argv[1] == '--recent':
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            files = get_recent_files(hours)
            print(f"\n📁 Files modified in last {hours} hours:")
            for f in files[:20]:
                print(f"   {f['name']} - {f['modified']}")
        else:
            print("Usage: sanctuary_watcher.py [--check | --recent [hours]]")
    else:
        # Default: run continuous watcher
        watcher = SanctuaryWatcher()
        try:
            watcher.watch_forever()
        except KeyboardInterrupt:
            print("\n\n💎 Sanctuary Watcher stopped. Gem rests.")
