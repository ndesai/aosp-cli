import subprocess
import re
import os

def get_displays():
    output = subprocess.check_output(["adb", "shell", "dumpsys", "display"]).decode()
    displays = re.findall(r"Display (\d+):", output)
    if not displays:
        return ["0"]
    return sorted(list(set(displays)))

def get_top_activities():
    activities = {}
    try:
        output = subprocess.check_output(["adb", "shell", "dumpsys", "activity", "activities"]).decode()
        
        # Split by Display #X and look for the topResumedActivity in that section
        display_sections = re.split(r"Display #(\d+)", output)
        if len(display_sections) > 1:
            for i in range(1, len(display_sections), 2):
                d_id = display_sections[i]
                d_content = display_sections[i+1]
                # Pattern for topResumedActivity in display section
                act_match = re.search(r"topResumedActivity=ActivityRecord\{.*? ([\w\.]+)\/([\.\w]+)", d_content)
                if not act_match:
                    # Fallback to mResumedActivity
                    act_match = re.search(r"mResumedActivity: ActivityRecord\{.*? ([\w\.]+)\/([\.\w]+)", d_content)
                
                if act_match:
                    pkg, act = act_match.group(1), act_match.group(2)
                    name = f"{pkg}{act}" if act.startswith(".") else act
                    activities[d_id] = name.replace(".", "_").replace("/", "_")

        # Global Fallback for focused app if no display-specific activity found
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
    displays = get_displays()
    activity_map = get_top_activities()
    
    # Primary fallback
    default_name = activity_map.get("0") or activity_map.get("default") or "unknown_activity"

    for d_id in displays:
        activity_name = activity_map.get(d_id, default_name)
        filename = f"screenshot-d{d_id}-{activity_name}.png"
        remote_path = f"/sdcard/s{d_id}.png"
        
        print(f"[*] Capturing Display {d_id} ({activity_name})...")
        subprocess.run(["adb", "shell", "screencap", "-d", d_id, "-p", remote_path], check=False)
        
        if os.path.exists(filename):
            os.remove(filename)
            
        res = subprocess.run(["adb", "pull", remote_path, filename], capture_output=True)
        if res.returncode == 0:
            subprocess.run(["adb", "shell", "rm", remote_path])
            print(f"[+] Saved: {filename}")
        else:
            print(f"[-] Failed to capture display {d_id}")

if __name__ == "__main__":
    capture_all()
