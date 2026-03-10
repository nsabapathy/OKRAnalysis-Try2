#!/usr/bin/env python3
"""
Validate OKR entries in the data file
Find entries that are missing required fields
"""

from pathlib import Path

def validate_okr_file(file_path: str):
    """Validate OKR file and find problematic entries"""
    
    required_fields = [
        'Team:',
        'Quarter:',
        'Objective:',
        'Key Result 1:',
        'Key Result 2:',
        'Key Result 3:',
        'Quality Level:',
        'Raw Text:'
    ]
    
    entries = []
    current_entry = {}
    entry_number = 0
    line_number = 0
    entry_start_line = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_number += 1
            line = line.strip()
            
            if line == "=== OKR ENTRY ===":
                if current_entry:
                    # Validate the previous entry
                    entry_number += 1
                    missing_fields = []
                    for field in required_fields:
                        field_key = field.replace(':', '').replace(' ', '_').lower()
                        if field_key not in current_entry:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        entries.append({
                            'entry_number': entry_number,
                            'start_line': entry_start_line,
                            'end_line': line_number - 1,
                            'missing_fields': missing_fields,
                            'found_fields': list(current_entry.keys())
                        })
                
                current_entry = {}
                entry_start_line = line_number
            
            elif line.startswith("Team:"):
                current_entry['team'] = line.replace("Team:", "").strip()
            
            elif line.startswith("Quarter:"):
                current_entry['quarter'] = line.replace("Quarter:", "").strip()
            
            elif line.startswith("Objective:"):
                current_entry['objective'] = line.replace("Objective:", "").strip()
            
            elif line.startswith("Key Result 1:"):
                current_entry['key_result_1'] = line.replace("Key Result 1:", "").strip()
            
            elif line.startswith("Key Result 2:"):
                current_entry['key_result_2'] = line.replace("Key Result 2:", "").strip()
            
            elif line.startswith("Key Result 3:"):
                current_entry['key_result_3'] = line.replace("Key Result 3:", "").strip()
            
            elif line.startswith("Quality Level:"):
                current_entry['quality_level'] = line.replace("Quality Level:", "").strip()
            
            elif line.startswith("Raw Text:"):
                current_entry['raw_text'] = line.replace("Raw Text:", "").strip()
        
        # Validate the last entry
        if current_entry:
            entry_number += 1
            missing_fields = []
            for field in required_fields:
                field_key = field.replace(':', '').replace(' ', '_').lower()
                if field_key not in current_entry:
                    missing_fields.append(field)
            
            if missing_fields:
                entries.append({
                    'entry_number': entry_number,
                    'start_line': entry_start_line,
                    'end_line': line_number,
                    'missing_fields': missing_fields,
                    'found_fields': list(current_entry.keys())
                })
    
    return entries, entry_number

def main():
    file_path = "./data/okr_samples_500.txt"
    
    print("=" * 80)
    print("OKR FILE VALIDATION")
    print("=" * 80)
    print(f"Validating: {file_path}")
    print()
    
    problematic_entries, total_entries = validate_okr_file(file_path)
    
    print(f"Total entries found: {total_entries}")
    print(f"Valid entries: {total_entries - len(problematic_entries)}")
    print(f"Problematic entries: {len(problematic_entries)}")
    print()
    
    if problematic_entries:
        print("=" * 80)
        print("PROBLEMATIC ENTRIES DETAILS")
        print("=" * 80)
        
        for entry in problematic_entries:
            print(f"\n❌ Entry #{entry['entry_number']}")
            print(f"   Lines: {entry['start_line']}-{entry['end_line']}")
            print(f"   Missing fields: {', '.join(entry['missing_fields'])}")
            print(f"   Found fields: {', '.join(entry['found_fields'])}")
            
            # Read and display the actual entry
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"\n   Content:")
                for i in range(entry['start_line'] - 1, min(entry['end_line'], len(lines))):
                    print(f"   {i+1:4d}| {lines[i].rstrip()}")
    else:
        print("✅ All entries are valid!")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
