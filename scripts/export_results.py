#!/usr/bin/env python3
"""
Export Results Script
Exports analysis results to various formats (CSV, Excel, JSON)
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.storage import ResultsStorage


def main():
    print("📤 Exporting analysis results...")
    print()
    
    storage = ResultsStorage()
    
    export_dir = Path("./exports")
    export_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("1. Exporting OKRs...")
    okrs = storage.get_all_okrs()
    if okrs:
        df = pd.DataFrame(okrs)
        
        csv_path = export_dir / f"okrs_{timestamp}.csv"
        df.to_csv(csv_path, index=False)
        print(f"   ✓ CSV: {csv_path}")
        
        excel_path = export_dir / f"okrs_{timestamp}.xlsx"
        df.to_excel(excel_path, index=False, engine='openpyxl')
        print(f"   ✓ Excel: {excel_path}")
    else:
        print("   ⚠️  No OKR data found")
    
    print("\n2. Exporting quality scores...")
    quality = storage.get_quality_scores()
    if quality:
        df = pd.DataFrame(quality)
        
        csv_path = export_dir / f"quality_scores_{timestamp}.csv"
        df.to_csv(csv_path, index=False)
        print(f"   ✓ CSV: {csv_path}")
        
        excel_path = export_dir / f"quality_scores_{timestamp}.xlsx"
        df.to_excel(excel_path, index=False, engine='openpyxl')
        print(f"   ✓ Excel: {excel_path}")
    else:
        print("   ⚠️  No quality data found")
    
    print("\n3. Exporting themes...")
    themes = storage.get_themes()
    if themes:
        df = pd.DataFrame(themes)
        
        csv_path = export_dir / f"themes_{timestamp}.csv"
        df.to_csv(csv_path, index=False)
        print(f"   ✓ CSV: {csv_path}")
        
        excel_path = export_dir / f"themes_{timestamp}.xlsx"
        df.to_excel(excel_path, index=False, engine='openpyxl')
        print(f"   ✓ Excel: {excel_path}")
    else:
        print("   ⚠️  No theme data found")
    
    print("\n4. Exporting alignment matrix...")
    alignment = storage.get_alignment_matrix()
    if alignment and alignment.get('teams'):
        teams = alignment['teams']
        matrix = alignment['matrix']
        
        df = pd.DataFrame(matrix, index=teams)
        
        csv_path = export_dir / f"alignment_matrix_{timestamp}.csv"
        df.to_csv(csv_path)
        print(f"   ✓ CSV: {csv_path}")
        
        excel_path = export_dir / f"alignment_matrix_{timestamp}.xlsx"
        df.to_excel(excel_path, engine='openpyxl')
        print(f"   ✓ Excel: {excel_path}")
    else:
        print("   ⚠️  No alignment data found")
    
    print("\n" + "=" * 80)
    print(f"✅ Export complete! Files saved to: {export_dir}")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Export error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
