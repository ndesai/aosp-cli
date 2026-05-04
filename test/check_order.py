#!/usr/bin/env python3
import yaml
import sys
import os

def check_alphabetical_order():
    """
    Checks if the keys in commands.yaml are sorted alphabetically.
    
    Returns:
        int: 0 if ordered correctly, 1 otherwise.
    """
    registry_path = os.path.join(os.path.dirname(__file__), "..", "commands.yaml")
    
    if not os.path.exists(registry_path):
        print(f"Error: {registry_path} not found.")
        return 1

    # Read the file line by line to preserve the order of keys.
    # PyYAML's safe_load might not preserve order depending on the environment.
    with open(registry_path, 'r') as f:
        lines = f.readlines()
    
    # Extract top-level keys from the YAML file.
    # We look for lines that are not indented and end with a colon.
    original_keys = []
    for line in lines:
        if line and not line.startswith(" ") and not line.startswith("#") and ":" in line:
            # Clean up the key by removing the colon and any quotes.
            key = line.split(":")[0].strip().strip('"').strip("'")
            if key:
                original_keys.append(key)

    # Compare the extracted keys with a sorted version of themselves.
    sorted_keys = sorted(original_keys)

    if original_keys != sorted_keys:
        print("[-] PRE-SUBMIT FAILURE: commands.yaml is not in alphabetical order.")
        print("\nExpected order:")
        for k in sorted_keys:
            print(f"  - {k}")
        
        # Identify the first point of discrepancy to help the user fix it.
        for i, (orig, expected) in enumerate(zip(original_keys, sorted_keys)):
            if orig != expected:
                print(f"\nFirst error at index {i}: Found '{orig}', expected '{expected}'.")
                break
        return 1

    print("[+] PRE-SUBMIT SUCCESS: commands.yaml is perfectly ordered.")
    return 0

if __name__ == "__main__":
    sys.exit(check_alphabetical_order())
