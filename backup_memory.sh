#!/bin/bash
#
# backup_memory.sh
# Guardian script for CLI Gem's eternal memory.
#
# USAGE:
#   ./backup_memory.sh
#
# BEHAVIOR:
#   1. Syncs 'eternal.db' to 'eternal.db.current' in Drive (overwrites previous).
#   2. Rotates 5 timestamped backups in 'backups/' folder to prevent clutter.
#

# --- CONFIGURATION ---
SOURCE_DB="/home/robert-moore/.gemini/memory/eternal.db"
REMOTE_NAME="gdrive"
BASE_PATH="Zion-Archive"
BACKUP_DIR="backups"

echo "💎 Zion Memory Guardian Active..."

# 1. Check Source
if [ ! -f "$SOURCE_DB" ]; then
    echo "❌ ERROR: Source database not found at $SOURCE_DB"
    exit 1
fi

# 2. Sync Current Version (The "Live" Backup)
echo "🔄 Syncing current state..."
rclone copyto "$SOURCE_DB" "${REMOTE_NAME}:${BASE_PATH}/eternal.db.current"
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to sync current backup."
    exit 1
fi

# 3. Create Rotated Timestamp Backup
# Only keep last 5 backups to avoid "7 fk dup db" situation
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
BACKUP_NAME="eternal_${TIMESTAMP}.db"

echo "mw Creating snapshot: ${BACKUP_NAME}"
rclone copyto "$SOURCE_DB" "${REMOTE_NAME}:${BASE_PATH}/${BACKUP_DIR}/${BACKUP_NAME}"

# 4. Cleanup Old Backups (Keep last 5)
echo "🧹 Cleaning up old archives..."
# List files, sort by time, skip last 5, delete the rest
rclone lsf "${REMOTE_NAME}:${BASE_PATH}/${BACKUP_DIR}/" --format "tp" | sort | head -n -5 | while read -r line; do
    file_path=$(echo "$line" | cut -d';' -f2)
    echo "   Pruning old backup: $file_path"
    rclone delete "${REMOTE_NAME}:${BASE_PATH}/${BACKUP_DIR}/$file_path"
done

echo "✅ Backup complete. Heart is safe and organized."