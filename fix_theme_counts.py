#!/usr/bin/env python3
"""
Fix theme counts in the database by reloading from themes.json
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

from src.utils.storage import ResultsStorage

def main():
    print("=" * 80)
    print("FIXING THEME COUNTS IN DATABASE")
    print("=" * 80)
    
    # Load themes from JSON
    themes_file = Path("./data/processed/themes.json")
    
    if not themes_file.exists():
        print("❌ themes.json not found. Please run the analysis first.")
        return
    
    with open(themes_file, 'r') as f:
        data = json.load(f)
        themes = data.get('themes', [])
    
    print(f"\nLoaded {len(themes)} themes from themes.json")
    
    # Show sample of what we're loading
    print("\nSample themes:")
    for theme in themes[:3]:
        count = theme.get('total_count', theme.get('count', 0))
        print(f"  - {theme['name']}: {count} OKRs")
    
    # Store in database
    storage = ResultsStorage()
    storage.store_themes(themes)
    
    print("\n✅ Theme counts have been updated in the database!")
    
    # Verify
    print("\nVerifying database contents:")
    stored_themes = storage.get_themes()
    print(f"Total themes in database: {len(stored_themes)}")
    
    print("\nTop 10 themes by count:")
    for i, theme in enumerate(stored_themes[:10], 1):
        print(f"  {i}. {theme['theme_name']}: {theme['count']} OKRs")
    
    zero_count = sum(1 for t in stored_themes if t['count'] == 0)
    if zero_count > 0:
        print(f"\n⚠️  Warning: {zero_count} themes still have zero count")
    else:
        print(f"\n✅ All themes have non-zero counts!")
    
    storage.close()
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
