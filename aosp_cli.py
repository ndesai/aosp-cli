#!/usr/bin/env python3
import argparse
import subprocess
import json
import os
import yaml

class AOSPTool:
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), "profiles.json")
    REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "commands.yaml")
    
    def __init__(self):
        self.registry = self.load_registry()

    def load_registry(self):
        if not os.path.exists(self.REGISTRY_PATH):
            print(f"[-] Registry file not found: {self.REGISTRY_PATH}")
            return {}
        with open(self.REGISTRY_PATH, 'r') as f:
            return yaml.safe_load(f)

    def execute(self, key, args_val="", silent=False):
        entry = self.registry.get(key)
        if not entry:
            if not silent: print(f"[-] Command '{key}' not found.")
            return False
        
        full_command = entry['command'].format(args=args_val)
        # Split by && but respect the sequence. 
        # Commands starting with 'adb ' are kept as is, others are prefixed with 'adb shell'
        for step in full_command.split("&&"):
            step = step.strip()
            if not step: continue
            
            if step.startswith("adb "):
                cmd = step.split(" ")
            else:
                cmd = ["adb", "shell"] + step.split(" ")
            
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
            print(f"[-] Profile '{name}' not found.")
            return
        
        profile = profiles[name]
        print(f"[!] Applying Profile: {name} ({profile.get('description', '')})")
        for cmd_key in profile.get("commands", []):
            self.execute(cmd_key, silent=True)
        print("[+] Profile applied successfully.")

    def search(self, query):
        print(f"\n[?] Searching for: '{query}'\n")
        q = query.lower()
        for key, data in self.registry.items():
            desc = data.get('description', '')
            tags = data.get('tags', [])
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

    # Commands that require arguments
    needs_args = ["record", "font-size", "battery-level", "link", "clear", "force-stop", "uninstall"]
    
    for key in tool.registry.keys():
        sp = subparsers.add_parser(key)
        if "{args}" in tool.registry[key].get('command', '') or key in needs_args:
            sp.add_argument("args", nargs="?", default="")

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
