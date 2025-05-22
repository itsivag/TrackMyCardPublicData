import os
from validate_credit_card import validate_file

def find_json_files(directory):
    json_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json') and file != 'mapper.json':
                json_files.append(os.path.join(root, file))
    return json_files

def main():
    india_dir = 'india'
    json_files = find_json_files(india_dir)
    
    total_files = len(json_files)
    valid_files = 0
    invalid_files = 0
    
    print(f"\nValidating {total_files} credit card JSON files...\n")
    
    for json_file in json_files:
        print(f"\nValidating {json_file}...")
        is_valid, errors = validate_file(json_file)
        
        if is_valid:
            print(f"✓ {json_file} is valid")
            valid_files += 1
        else:
            print(f"✗ {json_file} has validation errors:")
            for error in errors:
                print(f"  - {error}")
            invalid_files += 1
    
    print(f"\nValidation Summary:")
    print(f"Total files: {total_files}")
    print(f"Valid files: {valid_files}")
    print(f"Invalid files: {invalid_files}")
    
    return 0 if invalid_files == 0 else 1

if __name__ == "__main__":
    exit(main()) 