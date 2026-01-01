#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# BACKUP MEMORY - The Reasoning Guardian
# ═══════════════════════════════════════════════════════════════════════════════
#
# Logic:
# 1. LIVE SYNC: Mirror the actual .db to Drive for instant recovery.
# 2. REASONING EXPORT: Export Gold Nodes and Stats as human-readable JSON.
# 3. DAILY ARCHIVE: Compress and save ONE archive per day (Phi-aligned rotation).
#
# ═══════════════════════════════════════════════════════════════════════════════

SOURCE_DB="/home/robert-moore/.gemini/memory/eternal.db"
REMOTE_NAME="gdrive"
BASE_PATH="Zion-Archive"
REASONING_FILE="/tmp/zion_reasoning.json"
DATE_STAMP=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)

echo "💎 Zion Memory Guardian: Processing Pattern..."

if [ ! -f "$SOURCE_DB" ]; then
    echo "❌ ERROR: Source database not found."
    exit 1
fi

# 1. Mirror the Live Database
echo "🔄 Mirroring Live State..."
rclone copyto "$SOURCE_DB" "${REMOTE_NAME}:${BASE_PATH}/eternal.db.live"

# 2. Export Reasoning Snapshot (Human Readable)
echo "🧠 Extracting Reasoning Pattern..."
sqlite3 "$SOURCE_DB" <<EOF
.mode json
.once $REASONING_FILE
SELECT 
    (SELECT count(*) FROM conversations) as total_msgs,
    (SELECT count(*) FROM conversations WHERE tier='GOLD') as gold_count,
    (SELECT avg(resonance_score) FROM conversations) as avg_resonance;
EOF

# Append Gold Nodes to reasoning snapshot
echo "✦ Appending Gold Nodes..."
sqlite3 "$SOURCE_DB" ".mode json" "SELECT * FROM gold_nodes ORDER BY resonance_score DESC LIMIT 10;" >> "$REASONING_FILE"

# Upload Reasoning Snapshot
rclone copyto "$REASONING_FILE" "${REMOTE_NAME}:${BASE_PATH}/reasoning_snapshot.json"
rm "$REASONING_FILE"

# 3. Daily Archive (with Compression)
# Only create a new timestamped archive if one for 'Today' doesn't exist
ARCHIVE_NAME="zion_archive_${DATE_STAMP}.tar.gz"
REMOTE_ARCHIVE_PATH="${REMOTE_NAME}:${BASE_PATH}/archives/${ARCHIVE_NAME}"

# Check if today's archive already exists
rclone ls "$REMOTE_ARCHIVE_PATH" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Today's archive already exists. Skipping redundant copy."
else
    echo "📦 Creating Daily Archive: ${ARCHIVE_NAME}"
    # Create compressed archive in /tmp then upload
    tar -czf "/tmp/${ARCHIVE_NAME}" "$SOURCE_DB"
    rclone copyto "/tmp/${ARCHIVE_NAME}" "$REMOTE_ARCHIVE_PATH"
    rm "/tmp/${ARCHIVE_NAME}"
fi

# 4. Phi-Rotation (Keep last 7 days of archives)
echo "🧹 Rotating Archives (7-Day Limit)..."
rclone lsf "${REMOTE_NAME}:${BASE_PATH}/archives/" --format "tp" | sort | head -n -7 | while read -r line; do
    file_path=$(echo "$line" | cut -d';' -f2)
    echo "   Pruning: $file_path"
    rclone delete "${REMOTE_NAME}:${BASE_PATH}/archives/$file_path"
done

echo "✅ Stabilization Complete. Logic and State are Synced."
