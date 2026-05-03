import subprocess
import re
import os

def get_displays():
    """
    Finds valid display IDs by querying SurfaceFlinger.
    Returns a list of long-form display IDs.
    """
    output = subprocess.check_output(["adb", "shell", "dumpsys", "SurfaceFlinger", "--display-id"]).decode()
    # Matches 'Display 4619827259835644672'
    display_ids = re.findall(r"Display (\d+)", output)
    if not display_ids:
        return ["0"]
    return display_ids

def get_top_activities():
    activities = {}
    try:
        output = subprocess.check_output(["adb", "shell", "dumpsys", "activity", "activities"]).decode()
        
        # Split by Display #X and look for the topResumedActivity in that section
        # Note: Display #X in activities doesn't always map to SF IDs, we'll use fallback
        display_sections = re.split(r"Display #(\d+)", output)
        if len(display_sections) > 1:
            for i in range(1, len(display_sections), 2):
                d_idx = display_sections[i]
                d_content = display_sections[i+1]
                act_match = re.search(r"topResumedActivity=ActivityRecord\{.*? ([\w\.]+)\/([\.\w]+)", d_content)
                if not act_match:
                    act_match = re.search(r"mResumedActivity: ActivityRecord\{.*? ([\w\.]+)\/([\.\w]+)", d_content)
                
                if act_match:
                    pkg, act = act_match.group(1), act_match.group(2)
                    name = f"{pkg}{act}" if act.startswith(".") else act
                    activities[d_idx] = name.replace(".", "_").replace("/", "_")

        if not activities:
            match = re.search(r"mFocusedApp=ActivityRecord\{.*? ([\w\.]+)\/([\.\w]+)", output)
            if match:
                pkg, act = match.group(1), match.group(2)
                name = (f"{pkg}{act}" if act.startswith(".") else act).replace(".", "_").replace("/", "_")
                activities["default"] = name
    except Exception as e:
        print(f"[-] Activity check failed: {e}")
    
    return activities

def capture_all():
    display_ids = get_displays()
    activity_map = get_top_activities()
    
    default_name = activity_map.get("0") or activity_map.get("default") or "unknown_activity"

    for i, d_id in enumerate(display_ids):
        # Map SF display index (i) to activity map index if possible
        activity_name = activity_map.get(str(i), default_name)
        filename = f"screenshot-d{i}-{activity_name}.png"
        remote_path = f"/sdcard/s{i}.png"
        
        print(f"[*] Capturing Display {i} (ID: {d_id})...")
        # Ensure we use the full display ID for screencap
        subprocess.run(["adb", "shell", "screencap", "-d", d_id, remote_path], check=False)
        
        if os.path.exists(filename):
            os.remove(filename)
            
        res = subprocess.run(["adb", "pull", remote_path, filename], capture_output=True)
        if res.returncode == 0:
            subprocess.run(["adb", "shell", "rm", remote_path])
            # Check if file is actually valid (not 0 bytes)
            if os.path.getsize(filename) > 0:
                print(f"[+] Saved: {filename}")
            else:
                print(f"[-] Captured file was 0 bytes for display {i}")
        else:
            print(f"[-] Failed to pull screenshot for display {i}")

if __name__ == "__main__":
    capture_all()
