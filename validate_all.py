#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

def find_json_files():
    """Find all JSON files in the repository."""
    json_files = []
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    return json_files

def validate_file(file_path):
    """Run validation on a single file."""
    print(f"\nValidating {file_path}...")
    result = subprocess.run(['python3', 'validate_credit_card_json.py', file_path, '--verbose'],
                          capture_output=True, text=True)
    return result.returncode == 0, result.stdout

def main():
    json_files = find_json_files()
    if not json_files:
        print("No JSON files found in the repository.")
        sys.exit(1)

    print(f"Found {len(json_files)} JSON files to validate.")
    
    success_count = 0
    failed_files = []

    for file_path in json_files:
        success, output = validate_file(file_path)
        if success:
            success_count += 1
            print("✅ Validation successful")
        else:
            failed_files.append(file_path)
            print("❌ Validation failed")
            print(output)

    # Print summary
    print("\n=== Validation Summary ===")
    print(f"Total files: {len(json_files)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(failed_files)}")
    
    if failed_files:
        print("\nFailed files:")
        for file in failed_files:
            print(f"- {file}")
        sys.exit(1)
    else:
        print("\nAll files passed validation! 🎉")
        sys.exit(0)

if __name__ == "__main__":
    main() 