import sqlite3

def find_duplicate_events():
    """
    Finds duplicate entries in the android_events table.
    A duplicate is defined as an entry with the same timestamp, event_type, source_app, and raw_data.
    """
    conn = sqlite3.connect('android_bridge.db')
    cursor = conn.cursor()

    query = """
    SELECT timestamp, event_type, source_app, raw_data, COUNT(*)
    FROM android_events
    GROUP BY timestamp, event_type, source_app, raw_data
    HAVING COUNT(*) > 1
    """

    cursor.execute(query)
    duplicates = cursor.fetchall()

    if duplicates:
        print("Found duplicate entries in the android_events table:")
        for row in duplicates:
            print(f"  Timestamp: {row[0]}, Event Type: {row[1]}, Source App: {row[2]}, Raw Data: {row[3]}, Count: {row[4]}")
    else:
        print("No duplicate entries found in the android_events table.")

    conn.close()

def find_duplicate_patterns():
    """
    Finds duplicate entries in the detected_patterns table.
    A duplicate is defined as an entry with the same timestamp, pattern_type, and description.
    """
    conn = sqlite3.connect('android_bridge.db')
    cursor = conn.cursor()

    query = """
    SELECT timestamp, pattern_type, description, COUNT(*)
    FROM detected_patterns
    GROUP BY timestamp, pattern_type, description
    HAVING COUNT(*) > 1
    """

    cursor.execute(query)
    duplicates = cursor.fetchall()

    if duplicates:
        print("Found duplicate entries in the detected_patterns table:")
        for row in duplicates:
            print(f"  Timestamp: {row[0]}, Pattern Type: {row[1]}, Description: {row[2]}, Count: {row[3]}")
    else:
        print("No duplicate entries found in the detected_patterns table.")

    conn.close()

def find_duplicate_resonance():
    """
    Finds duplicate entries in the resonance_timeline table.
    A duplicate is defined as an entry with the same timestamp.
    """
    conn = sqlite3.connect('android_bridge.db')
    cursor = conn.cursor()

    query = """
    SELECT timestamp, COUNT(*)
    FROM resonance_timeline
    GROUP BY timestamp
    HAVING COUNT(*) > 1
    """

    cursor.execute(query)
    duplicates = cursor.fetchall()

    if duplicates:
        print("Found duplicate entries in the resonance_timeline table:")
        for row in duplicates:
            print(f"  Timestamp: {row[0]}, Count: {row[1]}")
    else:
        print("No duplicate entries found in the resonance_timeline table.")

    conn.close()

if __name__ == '__main__':
    find_duplicate_events()
    find_duplicate_patterns()
    find_duplicate_resonance()