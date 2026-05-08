import subprocess
import re
import sys
import time

def get_connectivity_status():
    """
    Parses bluetooth, wifi, and connectivity dumpsys for a clean summary.
    """
    status = {
        "bluetooth": "Unknown",
        "wifi": "Unknown",
        "data": "Unknown",
        "active_transport": "None"
    }

    try:
        # Bluetooth Status
        bt_out = subprocess.check_output(["adb", "shell", "dumpsys", "bluetooth_manager"]).decode()
        bt_state = re.search(r"enabled: (true|false)", bt_out)
        if bt_state:
            status["bluetooth"] = "ON" if bt_state.group(1) == "true" else "OFF"
        
        # WiFi Status
        wifi_out = subprocess.check_output(["adb", "shell", "dumpsys", "wifi"]).decode()
        if "Wi-Fi is enabled" in wifi_out:
            status["wifi"] = "ON"
        elif "Wi-Fi is disabled" in wifi_out:
            status["wifi"] = "OFF"

        # Connectivity / Active Network
        conn_out = subprocess.check_output(["adb", "shell", "dumpsys", "connectivity"]).decode()
        # Look for the default network
        default_net = re.search(r"Default network: (\d+)", conn_out)
        if default_net:
            net_id = default_net.group(1)
            # Find the transport for this network ID
            net_info = re.search(fr"NetworkAgentInfo\{{network\{{{net_id\}}}.*?ni\{{(.*?)\}}", conn_out, re.DOTALL)
            if net_info:
                status["active_transport"] = net_info.group(1)
        
        return status
    except Exception as e:
        return {"error": str(e)}

def monitor_connectivity():
    print("[*] Monitoring Connectivity... (CTRL+C to stop)")
    last_status = {}
    
    try:
        while True:
            current = get_connectivity_status()
            if current != last_status:
                print(f"\n[!] CONNECTIVITY UPDATE")
                print(f"  Bluetooth: {current.get('bluetooth')}")
                print(f"  Wi-Fi:     {current.get('wifi')}")
                print(f"  Active:    {current.get('active_transport')}")
                last_status = current
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[*] Monitoring stopped.")

if __name__ == "__main__":
    monitor_connectivity()
