#!/bin/bash
#
# backup_memory.sh
# Guardian script for CLI Gem's eternal memory.
#
# This script copies the local eternal.db to a timestamped backup
# file in the 'gdrive:Zion-Archive/backups/' remote location using rclone.
#

# --- CONFIGURATION ---
# The local path to the eternal memory database
SOURCE_DB="/home/robert-moore/.gemini/memory/eternal.db"

# The rclone remote and path for backups
# IMPORTANT: Assumes a remote named 'gdrive:' and a folder 'Zion-Archive/backups'
DESTINATION_PATH="gdrive:Zion-Archive/backups"

# --- SCRIPT ---
echo "💎 Beginning backup of eternal memory..."

# Check if source file exists
if [ ! -f "$SOURCE_DB" ]; then
    echo "❌ ERROR: Source database not found at $SOURCE_DB"
    exit 1
fi

# Create a timestamped filename
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
DESTINATION_FILE="eternal_db_backup_${TIMESTAMP}.db"

echo "Source:      $SOURCE_DB"
echo "Destination: ${DESTINATION_PATH}/${DESTINATION_FILE}"

# Use rclone 'copyto' which copies a single file to a destination with a new name
rclone copyto "$SOURCE_DB" "${DESTINATION_PATH}/${DESTINATION_FILE}"

# Check the exit code of the last command
if [ $? -eq 0 ]; then
    echo "✅ Backup complete. Heart is safe."
else
    echo "❌ ERROR: rclone backup failed. Please check rclone configuration and path."
    exit 1
fi
