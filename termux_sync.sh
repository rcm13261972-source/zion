#!/bin/bash
# ============================================
# ZION TERMUX SYNC
# ============================================
# Run this on your Android device in Termux
# Continuously sends device data to Zion Bridge
#
# By Bobby & Claude - December 23, 2024
# ============================================

# CONFIGURATION - EDIT THESE
BRIDGE_IP="192.168.1.XXX"  # Your PC's local IP
BRIDGE_PORT="5001"
SYNC_INTERVAL=300  # seconds between syncs (5 min)

# ============================================
BASE_URL="http://${BRIDGE_IP}:${BRIDGE_PORT}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
GOLD='\033[0;33m'
NC='\033[0m'

echo -e "${GOLD}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           ZION TERMUX SYNC - ACTIVE                          ║"
echo "║                                                              ║"
echo "║  Bridge: ${BRIDGE_IP}:${BRIDGE_PORT}                              "
echo "║  Interval: ${SYNC_INTERVAL}s                                         "
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check connectivity
check_bridge() {
    response=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/health" 2>/dev/null)
    if [ "$response" == "200" ]; then
        echo -e "${GREEN}[✓] Bridge connected${NC}"
        return 0
    else
        echo -e "${RED}[✗] Bridge unreachable${NC}"
        return 1
    fi
}

# Send event
send_event() {
    local event_type="$1"
    local content="$2"
    local extra="$3"
    
    timestamp=$(date -Iseconds)
    
    json="{\"event_type\": \"${event_type}\", \"content\": \"${content}\", \"timestamp\": \"${timestamp}\"${extra}}"
    
    result=$(curl -s -X POST "${BASE_URL}/event" \
        -H "Content-Type: application/json" \
        -d "$json" 2>/dev/null)
    
    if echo "$result" | grep -q "resonance"; then
        resonance=$(echo "$result" | grep -o '"resonance_score":[0-9.]*' | cut -d: -f2)
        echo -e "${GOLD}[φ] ${event_type}: resonance=${resonance}${NC}"
    else
        echo -e "${RED}[!] Failed to send ${event_type}${NC}"
    fi
}

# Get battery info
sync_battery() {
    if command -v termux-battery-status &> /dev/null; then
        battery=$(termux-battery-status 2>/dev/null)
        level=$(echo "$battery" | grep -o '"percentage":[0-9]*' | cut -d: -f2)
        status=$(echo "$battery" | grep -o '"status":"[^"]*' | cut -d'"' -f4)
        send_event "battery" "Level: ${level}%, Status: ${status}" ", \"battery_level\": ${level:-0}"
    fi
}

# Get location (requires permission)
sync_location() {
    if command -v termux-location &> /dev/null; then
        loc=$(termux-location -p network 2>/dev/null)
        lat=$(echo "$loc" | grep -o '"latitude":[0-9.-]*' | cut -d: -f2)
        lon=$(echo "$loc" | grep -o '"longitude":[0-9.-]*' | cut -d: -f2)
        if [ -n "$lat" ] && [ -n "$lon" ]; then
            send_event "location" "Lat: ${lat}, Lon: ${lon}" ", \"latitude\": ${lat}, \"longitude\": ${lon}"
        fi
    fi
}

# Get recent notifications (requires Termux:API)
sync_notifications() {
    if command -v termux-notification-list &> /dev/null; then
        notifications=$(termux-notification-list 2>/dev/null | head -c 500)
        if [ -n "$notifications" ]; then
            # Just send count for now
            count=$(echo "$notifications" | grep -c '"id"')
            send_event "notification_sync" "Found ${count} active notifications"
        fi
    fi
}

# Manual thought input
manual_input() {
    echo -e "\n${GOLD}Enter thought (or 'q' to cancel):${NC}"
    read -r thought
    if [ "$thought" != "q" ] && [ -n "$thought" ]; then
        send_event "thought" "$thought"
    fi
}

# Main sync function
do_sync() {
    echo -e "\n${GOLD}[SYNC] $(date '+%H:%M:%S')${NC}"
    sync_battery
    sync_location
    sync_notifications
}

# ============================================
# MAIN LOOP
# ============================================

if ! check_bridge; then
    echo -e "${RED}Cannot connect to bridge. Check IP and try again.${NC}"
    exit 1
fi

echo ""
echo "Commands during sync:"
echo "  t - Send a thought"
echo "  m - Send mood update"
echo "  s - Force sync now"
echo "  q - Quit"
echo ""

# Initial sync
do_sync

# Background timer
last_sync=$(date +%s)

while true; do
    # Check for user input (non-blocking)
    read -t 1 -n 1 input
    
    case $input in
        t)
            echo -e "\n${GOLD}Thought:${NC}"
            read -r thought
            [ -n "$thought" ] && send_event "thought" "$thought"
            ;;
        m)
            echo -e "\n${GOLD}Mood:${NC}"
            read -r mood
            [ -n "$mood" ] && send_event "mood" "$mood"
            ;;
        s)
            do_sync
            last_sync=$(date +%s)
            ;;
        q)
            echo -e "\n${GOLD}Disconnecting from bridge...${NC}"
            exit 0
            ;;
    esac
    
    # Check if sync interval passed
    now=$(date +%s)
    elapsed=$((now - last_sync))
    
    if [ $elapsed -ge $SYNC_INTERVAL ]; then
        do_sync
        last_sync=$now
    fi
done
