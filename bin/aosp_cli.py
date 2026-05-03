#!/usr/bin/env python3
import argparse
import subprocess
import os
import time
import yaml

try:
    import argcomplete
except ImportError:
    argcomplete = None


def get_installed_packages():
    """
    Fetch list of installed packages from the device via adb.

    Returns:
        list: A list of package names.
    """
    try:
        # Fetch package list from adb with a short timeout
        res = subprocess.run(
            ["adb", "shell", "pm", "list", "packages"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if res.returncode == 0:
            return [
                line.replace("package:", "").strip()
                for line in res.stdout.splitlines()
                if line.startswith("package:")
            ]
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return []


def package_completer(prefix, **kwargs):
    """
    Fetcher for argcomplete to list installed packages from the device.
    """
    packages = get_installed_packages()
    return [p for p in packages if p.startswith(prefix)]


class AOSPTool:
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "profiles.yaml")
    REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "..", "commands.yaml")

    def __init__(self):
        self.registry = self.load_registry()

    def load_registry(self):
        if not os.path.exists(self.REGISTRY_PATH):
            print(f"[-] Registry file not found: {self.REGISTRY_PATH}")
            return {}
        with open(self.REGISTRY_PATH, "r") as f:
            return yaml.safe_load(f)

    def execute(self, key, args_val="", silent=False):
        entry = self.registry.get(key)
        if not entry:
            if not silent:
                print(f"[-] Command '{key}' not found.")
            return False

        # Special handler for recording
        if key == "record":
            return self.record_flow(args_val)

        # Fuzzy package resolution for app-tagged commands
        if "app" in entry.get("tags", []) and args_val and not args_val.startswith("-"):
            resolved = self.resolve_package(args_val)
            if not resolved:
                return False
            args_val = resolved

        full_command = entry["command"].format(
            args=args_val, bin_dir=os.path.dirname(__file__)
        )
        # Split by && but respect the sequence.
        # Commands starting with 'adb ' are kept as is, others are prefixed with 'adb shell'
        for step in full_command.split("&&"):
            step = step.strip()
            if not step:
                continue

            if step.startswith("adb "):
                cmd = step.split()
            elif step.startswith("python3 "):
                cmd = step.split()
            else:
                cmd = ["adb", "shell"] + step.split()

            if not silent:
                print(f"[>] {' '.join(cmd)}")
            subprocess.run(cmd, capture_output=silent)
        return True

    def load_profiles(self):
        if not os.path.exists(self.CONFIG_PATH):
            return {}
        with open(self.CONFIG_PATH, "r") as f:
            return yaml.safe_load(f)

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
        """
        Search for commands matching a query in keys, descriptions, or tags.
        """
        print(f"\n[?] Searching for: '{query}'\n")
        q = query.lower()
        for key, data in self.registry.items():
            desc = data.get("description", "")
            tags = data.get("tags", [])
            if (
                q in key.lower()
                or q in desc.lower()
                or any(q in t.lower() for t in tags)
            ):
                print(f"  \033[1m{key:15}\033[0m - {desc}")
        print()

    def teach(self, key, args_val=""):
        """
        Display the underlying command for a shorthand.

        Args:
            key (str): The shorthand command key.
            args_val (str): Optional arguments for the command.
        """
        entry = self.registry.get(key)
        if not entry:
            print(f"[-] Command '{key}' not found.")
            return

        # Fuzzy package resolution for app-tagged commands
        if "app" in entry.get("tags", []) and args_val and not args_val.startswith("-"):
            resolved = self.resolve_package(args_val)
            if resolved:
                args_val = resolved

        # Replace placeholders like {args} and {bin_dir}
        full_command = entry["command"].format(
            args=args_val, bin_dir=os.path.dirname(__file__)
        )
        print(full_command)

    def resolve_package(self, query):
        """
        Resolve a partial package name to a full one.
        Prompts for disambiguation if multiple matches are found.
        """
        packages = get_installed_packages()

        # Look for exact match first
        if query in packages:
            return query

        matches = [p for p in packages if query.lower() in p.lower()]

        if not matches:
            print(f"[-] No packages found matching '{query}'.")
            return None

        if len(matches) == 1:
            return matches[0]

        print(f"\n[?] Multiple packages match '{query}':")
        for i, pkg in enumerate(matches, 1):
            print(f"  {i}) {pkg}")

        try:
            prompt = f"Select (1-{len(matches)}) or 'q' to quit: "
            choice = input(prompt).strip().lower()
            if choice == "q":
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(matches):
                return matches[idx]
        except (ValueError, EOFError, KeyboardInterrupt):
            print("\n[-] Cancelled.")

        return None
    def record_flow(self, local_filename):
        """
        Special handler for screen recording that pulls the file locally.
        """
        local_filename = local_filename or "recording.mp4"
        if not local_filename.endswith(".mp4"):
            local_filename += ".mp4"

        remote_path = "/sdcard/aosp_record_temp.mp4"
        cmd = ["adb", "shell", "screenrecord", remote_path]

        print(f"[!] Starting screenrecord on device...")
        print(f"[!] Target local file: {local_filename}")
        print("[!] Press CTRL+C to stop recording.")

        try:
            # We don't capture output here so user can see adb errors if any
            subprocess.run(cmd)
        except KeyboardInterrupt:
            # CTRL+C was pressed. screenrecord on device will receive SIGINT and stop.
            print("\n[!] Stopping recording...")

        # Add a small delay to ensure the file is flushed on the device
        time.sleep(1)

        print(f"[>] Pulling recording from device...")
        pull_res = subprocess.run(
            ["adb", "pull", remote_path, local_filename], capture_output=True
        )

        if pull_res.returncode == 0:
            print(f"[+] Successfully saved recording to: {local_filename}")
            subprocess.run(["adb", "shell", "rm", remote_path], capture_output=True)
        else:
            print(f"[-] Failed to pull recording: {pull_res.stderr.decode().strip()}")

        return True


def main():
    tool = AOSPTool()
    parser = argparse.ArgumentParser(
        description="AOSP CLI: A tool to streamline Android OS testing and debugging"
    )
    subparsers = parser.add_subparsers(dest="cmd")

    subparsers.add_parser("search", help="Search commands").add_argument("query")
    subparsers.add_parser("profile", help="Run a profile").add_argument("name")
    subparsers.add_parser("list-profiles", help="List available profiles")

    teach_parser = subparsers.add_parser(
        "teach", help="Show the exact command that a shorthand executes"
    )
    teach_parser.add_argument("name", help="The shorthand command to learn about")
    teach_parser.add_argument(
        "extra_args", nargs="*", help="Optional arguments for the shorthand"
    )

    # Commands that require arguments
    needs_args = [
        "record",
        "font-size",
        "battery-level",
        "link",
        "clear",
        "force-stop",
        "uninstall",
    ]

    for key in tool.registry.keys():
        sp = subparsers.add_parser(key)
        if "{args}" in tool.registry[key].get("command", "") or key in needs_args:
            arg = sp.add_argument("args", nargs="?", default="")
            # Enable package autocomplete for commands tagged with 'app'
            if argcomplete and "app" in tool.registry[key].get("tags", []):
                arg.completer = package_completer

    if argcomplete:
        argcomplete.autocomplete(parser)

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
    elif args.cmd == "teach":
        tool.teach(args.name, " ".join(args.extra_args))
    else:
        tool.execute(args.cmd, getattr(args, "args", ""))


if __name__ == "__main__":
    main()
