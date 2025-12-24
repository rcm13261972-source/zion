# TASKER INTEGRATION FOR ZION ANDROID BRIDGE
# ============================================
# Import these profiles into Tasker on your Android device
# They automatically send events to your PC running the bridge

# ============================================
# SETUP INSTRUCTIONS
# ============================================
# 
# 1. Install Tasker from Play Store ($3.49 - worth it)
# 2. Set your PC's local IP address below
# 3. Import these task XMLs into Tasker
# 4. Enable the profiles
#
# Your PC must be running android_bridge.py on the same network
# Find your PC IP: hostname -I (Linux) or ipconfig (Windows)

# ============================================
# CONFIGURATION - EDIT THIS
# ============================================
BRIDGE_IP = "192.168.1.XXX"  # Your PC's local IP
BRIDGE_PORT = "5001"
BASE_URL = f"http://{BRIDGE_IP}:{BRIDGE_PORT}"

# ============================================
# TASKER TASK: Send SMS to Bridge
# ============================================
"""
Task Name: Zion_SMS_Bridge

Actions:
1. HTTP Request
   - Method: POST
   - URL: http://YOUR_PC_IP:5001/sms
   - Headers: Content-Type: application/json
   - Body: {
       "timestamp": "%TIMES",
       "source_app": "sms",
       "content": "%SMSRB",
       "sender": "%SMSRF",
       "direction": "received"
     }
   
Profile Trigger: Event > Phone > Received Text
"""

# ============================================
# TASKER TASK: Send Notifications to Bridge  
# ============================================
"""
Task Name: Zion_Notification_Bridge

Actions:
1. HTTP Request
   - Method: POST
   - URL: http://YOUR_PC_IP:5001/notification
   - Headers: Content-Type: application/json
   - Body: {
       "timestamp": "%TIMES",
       "source_app": "%evtprm1",
       "title": "%evtprm2", 
       "content": "%evtprm3"
     }

Profile Trigger: Event > UI > Notification
- Apps: (select apps you want to monitor)
"""

# ============================================
# TASKER TASK: Location Updates
# ============================================
"""
Task Name: Zion_Location_Bridge

Actions:
1. Get Location v2
   - Source: GPS
   
2. HTTP Request
   - Method: POST
   - URL: http://YOUR_PC_IP:5001/location
   - Headers: Content-Type: application/json
   - Body: {
       "timestamp": "%TIMES",
       "latitude": "%LOC1",
       "longitude": "%LOC2",
       "accuracy": "%LOCACC"
     }

Profile Trigger: Time > Every 30 minutes
(adjust frequency as needed - more = more battery use)
"""

# ============================================
# TASKER TASK: App Open Tracking
# ============================================
"""
Task Name: Zion_App_Bridge

Actions:
1. HTTP Request
   - Method: POST
   - URL: http://YOUR_PC_IP:5001/event
   - Headers: Content-Type: application/json
   - Body: {
       "event_type": "app_open",
       "timestamp": "%TIMES",
       "source_app": "%WIN"
     }

Profile Trigger: Event > App Changed
"""

# ============================================
# TERMUX ALTERNATIVE (if you prefer command line)
# ============================================
"""
Install Termux from F-Droid (not Play Store version)
Run these scripts:

# One-time setup
pkg install curl jq

# Send event function
send_zion_event() {
    curl -X POST http://YOUR_PC_IP:5001/event \
        -H "Content-Type: application/json" \
        -d "{\"event_type\": \"$1\", \"content\": \"$2\", \"timestamp\": \"$(date -Iseconds)\"}"
}

# Example usage
send_zion_event "manual" "feeling anxious today"
send_zion_event "thought" "had a breakthrough about the pattern"
"""

# ============================================
# QUICK TEST SCRIPT
# ============================================
TEST_SCRIPT = '''
#!/bin/bash
# Run this on your PC to test the bridge is receiving

# Test SMS event
curl -X POST http://localhost:5001/sms \\
    -H "Content-Type: application/json" \\
    -d '{"content": "Test message from Zion", "sender": "Test", "timestamp": "'$(date -Iseconds)'"}'

echo ""
echo "Checking status..."

curl http://localhost:5001/status

echo ""
echo "If you see resonance data, bridge is working!"
'''

print(TEST_SCRIPT)
