import subprocess
import time
import re
import sys

def parse_notifications(output):
    """
    Parses 'dumpsys notification' output for active records.
    """
    notifications = []
    # Match NotificationRecord blocks
    records = re.split(r"NotificationRecord\(", output)
    for record in records[1:]:
        try:
            # Basic metadata
            pkg_match = re.search(r"pkg=([\w\.]+)", record)
            user_match = re.search(r"user=UserHandle\{(\d+)\}", record)
            imp_match = re.search(r"importance=(\d+)", record)
            
            # Content extras
            title_match = re.search(r"android\.title=String \[length=\d+\] (.*)", record)
            if not title_match: # Simple string format
                 title_match = re.search(r"android\.title=(.*)", record)
            
            text_match = re.search(r"android\.text=String \[length=\d+\] (.*)", record)
            if not text_match:
                text_match = re.search(r"android\.text=(.*)", record)

            category_match = re.search(r"category=([\w\.]+)", record)

            if pkg_match:
                notifications.append({
                    "pkg": pkg_match.group(1),
                    "user": user_match.group(1) if user_match else "0",
                    "importance": imp_match.group(1) if imp_match else "0",
                    "title": title_match.group(1).strip() if title_match else "None",
                    "text": text_match.group(1).strip() if text_match else "None",
                    "category": category_match.group(1) if category_match else "None"
                })
        except:
            continue
    return notifications

def monitor_notifications():
    """
    Monitor notifications by polling dumpsys and printing differences.
    """
    print("[*] Monitoring notifications... (CTRL+C to stop)")
    seen_ids = set()
    
    try:
        while True:
            output = subprocess.check_output(["adb", "shell", "dumpsys", "notification"]).decode()
            current_notes = parse_notifications(output)
            
            for note in current_notes:
                # Create a unique-ish ID based on content to detect "new" ones in poll
                note_id = f"{note['pkg']}|{note['title']}|{note['text']}"
                if note_id not in seen_ids:
                    print(f"\n[!] NEW NOTIFICATION")
                    print(f"  Package:  {note['pkg']}")
                    print(f"  Title:    {note['title']}")
                    print(f"  Text:     {note['text']}")
                    print(f"  Category: {note['category']}")
                    print(f"  Imp:      {note['importance']}")
                    seen_ids.add(note_id)
            
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[*] Monitoring stopped.")

if __name__ == "__main__":
    monitor_notifications()
