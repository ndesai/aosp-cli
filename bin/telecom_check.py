import subprocess
import re
import json
import sys

def check_telecom():
    """
    Parses 'dumpsys telecom' to find active/dialing/ringing calls and metadata.
    """
    try:
        output = subprocess.check_output(["adb", "shell", "dumpsys", "telecom"]).decode()
        
        # Focus on the mCalls section
        calls_match = re.search(r"mCalls:\s*(.*?)\nmCallAudioManager:", output, re.DOTALL)
        if not calls_match:
            print("[+] Calls: 0")
            return

        call_lines = calls_match.group(1).strip().split('\n')
        active_calls = []

        for line in call_lines:
            # Match pattern: [Call id=TC@1, state=DIALING, ..., handle=tel:*****34, ...]
            # Using flexible regex to catch various formats
            call_id = re.search(r"id=([\w@]+)", line)
            state = re.search(r"state=([\w]+)", line)
            handle = re.search(r"handle=([\w:\*]+)", line)
            is_voip = "voip=true" in line
            
            if call_id and state:
                metadata = {
                    "id": call_id.group(1),
                    "state": state.group(1),
                    "handle": handle.group(1) if handle else "unknown",
                    "type": "VOIP" if is_voip else "CS"
                }
                active_calls.append(metadata)

        if not active_calls:
            print("[+] Calls: 0")
            return

        print(f"[+] Active Calls: {len(active_calls)}")
        for call in active_calls:
            print(f"  - ID: {call['id']} | State: {call['state']} | Handle: {call['handle']} | Type: {call['type']}")
            
    except Exception as e:
        print(f"[-] Failed to check telecom status: {e}")

if __name__ == "__main__":
    check_telecom()
