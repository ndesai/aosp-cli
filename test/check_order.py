#!/usr/bin/env python3
import yaml
import sys
import os

def check_alphabetical_order():
    registry_path = os.path.join(os.path.dirname(__file__), "commands.yaml")
    
    if not os.path.exists(registry_path):
        print(f"Error: {registry_path} not found.")
        return 1

    with open(registry_path, 'r') as f:
        # Load keys from the raw file lines to check original order, 
        # as yaml.safe_load() might auto-sort depending on version/implementation
        lines = f.readlines()
    
    # Extract keys (lines that aren't indented and end in ':')
    original_keys = []
    for line in lines:
        if line and not line.startswith(" ") and ":" in line:
            key = line.split(":")[0].strip().strip('"').strip("'")
            if key:
                original_keys.append(key)

    sorted_keys = sorted(original_keys)

    if original_keys != sorted_keys:
        print("[-] PRE-SUBMIT FAILURE: commands.yaml is not in alphabetical order.")
        print("\nExpected order:")
        for k in sorted_keys:
            print(f"  - {k}")
        
        # Determine the first discrepancy for helpful output
        for i, (orig, expected) in enumerate(zip(original_keys, sorted_keys)):
            if orig != expected:
                print(f"\nFirst error at index {i}: Found '{orig}', expected '{expected}'.")
                break
        return 1

    print("[+] PRE-SUBMIT SUCCESS: commands.yaml is perfectly ordered.")
    return 0

if __name__ == "__main__":
    sys.exit(check_alphabetical_order())
