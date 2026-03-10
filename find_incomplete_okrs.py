#!/usr/bin/env python3
"""
Find incomplete OKR entries - entries that have the marker but missing fields
"""

from pathlib import Path

def find_incomplete_entries(file_path: str):
    """Find entries with missing required fields"""
    
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
    
    incomplete_entries = []
    current_entry_lines = []
    current_entry_fields = set()
    entry_number = 0
    entry_start_line = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line_number, line in enumerate(lines, 1):
        line_stripped = line.strip()
        
        if line_stripped == "=== OKR ENTRY ===":
            # Check if previous entry was complete
            if entry_number > 0:
                missing_fields = []
                for field in required_fields:
                    if field not in current_entry_fields:
                        missing_fields.append(field)
                
                if missing_fields:
                    incomplete_entries.append({
                        'entry_number': entry_number,
                        'start_line': entry_start_line,
                        'end_line': line_number - 1,
                        'missing_fields': missing_fields,
                        'found_fields': list(current_entry_fields),
                        'content_lines': current_entry_lines
                    })
            
            # Start new entry
            entry_number += 1
            entry_start_line = line_number
            current_entry_lines = [line]
            current_entry_fields = set()
        
        else:
            current_entry_lines.append(line)
            # Check which field this line belongs to
            for field in required_fields:
                if line_stripped.startswith(field):
                    current_entry_fields.add(field)
    
    # Check the last entry
    if entry_number > 0:
        missing_fields = []
        for field in required_fields:
            if field not in current_entry_fields:
                missing_fields.append(field)
        
        if missing_fields:
            incomplete_entries.append({
                'entry_number': entry_number,
                'start_line': entry_start_line,
                'end_line': len(lines),
                'missing_fields': missing_fields,
                'found_fields': list(current_entry_fields),
                'content_lines': current_entry_lines
            })
    
    return incomplete_entries, entry_number

def main():
    file_path = "./data/okr_samples_500.txt"
    
    print("=" * 80)
    print("FINDING INCOMPLETE OKR ENTRIES")
    print("=" * 80)
    print(f"Analyzing: {file_path}")
    print()
    
    incomplete_entries, total_entries = find_incomplete_entries(file_path)
    
    print(f"Total OKR markers found: {total_entries}")
    print(f"Complete entries: {total_entries - len(incomplete_entries)}")
    print(f"Incomplete entries: {len(incomplete_entries)}")
    print()
    
    if incomplete_entries:
        print("=" * 80)
        print("INCOMPLETE ENTRIES DETAILS")
        print("=" * 80)
        
        for entry in incomplete_entries:
            print(f"\n❌ Entry #{entry['entry_number']}")
            print(f"   Lines: {entry['start_line']}-{entry['end_line']}")
            print(f"   Missing fields: {', '.join(entry['missing_fields'])}")
            print(f"   Found fields: {', '.join(entry['found_fields'])}")
            
            print(f"\n   Full Content:")
            for i, line in enumerate(entry['content_lines'], entry['start_line']):
                print(f"   {i:4d}| {line.rstrip()}")
            print()
    else:
        print("✅ All entries are complete!")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
