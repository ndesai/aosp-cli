import subprocess
import re
import os

def get_displays():
    # Capture display IDs from dumpsys
    # Typically: Display 0: ..., Display 1: ...
    output = subprocess.check_output(["adb", "shell", "dumpsys", "display"]).decode()
    displays = re.findall(r"Display (\d+):", output)
    if not displays:
        # Fallback to display ID 0 if regex fails but device exists
        return ["0"]
    return displays

def get_top_activity():
    # Usually looking for: mResumedActivity: ActivityRecord{... u0 com.android.settings/.Settings t123}
    # Or: mFocusedActivity: ActivityRecord{...}
    try:
        output = subprocess.check_output(["adb", "shell", "dumpsys", "activity", "activities"]).decode()
        match = re.search(r"mResumedActivity: ActivityRecord\{.*? ([\w\.]+)\/([\.\w]+)", output)
        if match:
            pkg = match.group(1)
            activity = match.group(2)
            # Remove leading dot if present
            if activity.startswith("."):
                activity = pkg + activity
            return activity.replace(".", "_")
    except:
        pass
    return "unknown_activity"

def capture_all():
    displays = get_displays()
    top_activity = get_top_activity()
    
    for d_id in displays:
        filename = f"screenshot-d{d_id}-{top_activity}.png"
        remote_path = f"/sdcard/s{d_id}.png"
        
        print(f"[*] Capturing Display {d_id}...")
        # screencap -d <id> -p <path>
        subprocess.run(["adb", "shell", "screencap", "-d", d_id, "-p", remote_path])
        subprocess.run(["adb", "pull", remote_path, filename])
        subprocess.run(["adb", "shell", "rm", remote_path])
        print(f"[+] Saved: {filename}")

if __name__ == "__main__":
    capture_all()
