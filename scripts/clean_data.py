#!/usr/bin/env python3
"""
Clean Data Script
Removes generated data and resets the system
"""

import shutil
from pathlib import Path


def main():
    print("🧹 Cleaning generated data...")
    print()
    
    paths_to_clean = [
        "./data/chroma_db",
        "./data/processed",
        "./data/okr_results.db"
    ]
    
    for path_str in paths_to_clean:
        path = Path(path_str)
        
        if path.is_dir():
            shutil.rmtree(path)
            print(f"   ✓ Removed directory: {path}")
        elif path.is_file():
            path.unlink()
            print(f"   ✓ Removed file: {path}")
        else:
            print(f"   - Not found: {path}")
    
    Path("./data/processed").mkdir(parents=True, exist_ok=True)
    print()
    print("✅ Cleanup complete!")
    print()
    print("Run analysis again with: python scripts/run_analysis.py")


if __name__ == "__main__":
    main()
