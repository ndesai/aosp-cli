#!/usr/bin/env python3
import argparse
import subprocess
import json
import os

class AOSPTool:
    CONFIG_PATH = "/home/nd/workspace/profiles.json"
    
    REGISTRY = {
        "screenshot": ("screencap -p /sdcard/s.png && adb pull /sdcard/s.png . && adb shell rm /sdcard/s.png", "Capture screen, pull file, and cleanup", ["image", "capture"]),
        "record": ("screenrecord /sdcard/v.mp4", "Record screen (CTRL+C to stop) and pull file", ["video", "record"]),
        "dark": ("settings put secure ui_night_mode 2 && am broadcast -a android.intent.action.CONFIGURATION_CHANGED", "Enable dark mode", ["theme"]),
        "light": ("settings put secure ui_night_mode 1 && am broadcast -a android.intent.action.CONFIGURATION_CHANGED", "Enable light mode", ["theme"]),
        "clock-on": ("settings put secure clock_seconds 1", "Show seconds in clock", ["time"]),
        "clock-off": ("settings put secure clock_seconds 0", "Hide seconds in clock", ["time"]),
        "no-anim": ("settings put global window_animation_scale 0 && settings put global transition_animation_scale 0 && settings put global animator_duration_scale 0", "Disable animations", ["speed"]),
        "anim-on": ("settings put global window_animation_scale 1 && settings put global transition_animation_scale 1 && settings put global animator_duration_scale 1", "Enable animations", ["ui"]),
        "layout-on": ("setprop debug.layout true && service call activity 51", "Show layout bounds", ["debug"]),
        "layout-off": ("setprop debug.layout false && service call activity 51", "Hide layout bounds", ["ui"]),
        "taps-on": ("settings put system show_touches 1", "Show touch feedback", ["touches"]),
        "taps-off": ("settings put system show_touches 0", "Hide touch feedback", ["touches"]),
        "pointer-on": ("settings put system pointer_location 1", "Show touch coordinates", ["debug"]),
        "pointer-off": ("settings put system pointer_location 0", "Hide touch coordinates", ["input"]),
        "stay-awake": ("settings put global stay_on_while_plugged_in 3", "Keep screen on while charging", ["power"]),
        "sleep-normal": ("settings put global stay_on_while_plugged_in 0", "Default sleep behavior", ["power"]),
        "font-size": ("settings put system font_scale {args}", "Set font scale", ["accessibility"]),
        "reboot": ("reboot", "Normal reboot", ["power"]),
        "bootloader": ("reboot bootloader", "Reboot to bootloader", ["flashing"]),
        "remount": ("adb root && adb remount", "Root and remount system", ["root"]),
        "ip": ("ip addr show wlan0", "Show device IP", ["network"]),
        "uninstall": ("pm uninstall {args}", "Uninstall app", ["app"]),
        "clear": ("pm clear {args}", "Clear app data", ["app"]),
        "force-stop": ("am force-stop {args}", "Force stop app", ["app"]),
        "link": ("am start -a android.intent.action.VIEW -d {args}", "Open deep link", ["intent"]),
        "log-clear": ("logcat -c", "Clear logcat", ["debug"]),
        "log-crash": ("logcat *:E", "Show only errors", ["debug"]),
        "key-back": ("input keyevent 4", "Back button", ["input"]),
        "key-home": ("input keyevent 3", "Home button", ["input"])
    }

    def execute(self, key, args_val="", silent=False):
        entry = self.REGISTRY.get(key)
        if not entry:
            if not silent: print(f"[-] Command '{key}' not found.")
            return False
        
        full_command = entry[0].format(args=args_val)
        for step in full_command.split("&&"):
            step = step.strip()
            cmd = step.split(" ") if step.startswith("adb ") else ["adb", "shell"] + step.split(" ")
            if not silent: print(f"[>] {' '.join(cmd)}")
            subprocess.run(cmd, capture_output=silent)
        return True

    def load_profiles(self):
        if not os.path.exists(self.CONFIG_PATH):
            return {}
        with open(self.CONFIG_PATH, 'r') as f:
            return json.load(f)

    def run_profile(self, name):
        profiles = self.load_profiles()
        if name not in profiles:
            print(f"[-] Profile '{name}' not found in profiles.json.")
            return
        
        profile = profiles[name]
        print(f"[!] Applying Profile: {name} ({profile.get('description', '')})")
        for cmd_key in profile.get("commands", []):
            self.execute(cmd_key, silent=True)
        print("[+] Profile applied successfully.")

    def search(self, query):
        print(f"\n[?] Searching for: '{query}'\n")
        q = query.lower()
        for key, (cmd, desc, tags) in self.REGISTRY.items():
            if q in key.lower() or q in desc.lower() or any(q in t.lower() for t in tags):
                print(f"  \033[1m{key:15}\033[0m - {desc}")
        print()

def main():
    tool = AOSPTool()
    parser = argparse.ArgumentParser(description="AOSP-CLI: Lightweight. Extensible. Iconic.")
    subparsers = parser.add_subparsers(dest="cmd")

    subparsers.add_parser("search", help="Search commands").add_argument("query")
    subparsers.add_parser("profile", help="Run a profile").add_argument("name")
    subparsers.add_parser("list-profiles", help="List available profiles")

    needs_args = ["record", "font-size", "battery-level", "link", "clear", "force-stop", "uninstall"]
    for key in tool.REGISTRY.keys():
        sp = subparsers.add_parser(key)
        if key in needs_args: sp.add_argument("args", nargs="?", default="")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return

    if args.cmd == "search":
        tool.search(args.query)
    elif args.cmd == "profile":
        tool.run_profile(args.name)
    elif args.cmd == "list-profiles":
        profiles = tool.load_profiles()
        for name, data in profiles.items():
            print(f"  \033[1m{name:10}\033[0m - {data.get('description')}")
    else:
        tool.execute(args.cmd, getattr(args, "args", ""))

if __name__ == "__main__":
    main()
