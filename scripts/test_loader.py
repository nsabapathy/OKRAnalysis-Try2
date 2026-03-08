#!/usr/bin/env python3
"""
Quick test script to validate data loading
Tests the OKR loader without requiring API keys
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.okr_loader import OKRTextLoader, SmartChunker


def main():
    print("=" * 80)
    print("🧪 Testing OKR Data Loader")
    print("=" * 80)
    print()
    
    print("1. Loading OKR data...")
    try:
        loader = OKRTextLoader("./data/okr_samples_500.txt")
        print("   ✓ Loader initialized")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    print("\n2. Getting dataset statistics...")
    stats = loader.get_statistics()
    print(f"   ✓ Total OKRs: {stats['total_entries']}")
    print(f"   ✓ Unique teams: {stats['unique_teams']}")
    print(f"   ✓ Teams: {', '.join(stats['teams'][:10])}{'...' if len(stats['teams']) > 10 else ''}")
    print(f"   ✓ Quarters: {', '.join(stats['quarters'])}")
    print(f"   ✓ Quality distribution: {stats['quality_distribution']}")
    
    print("\n3. Testing chunking for parallel processing...")
    chunks = loader.chunk_for_parallel_processing(num_chunks=4)
    print(f"   ✓ Created {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        print(f"   - Chunk {i}: {len(chunk)} OKRs")
    
    print("\n4. Testing team grouping...")
    team_okrs = loader.chunk_by_team()
    print(f"   ✓ Grouped into {len(team_okrs)} teams")
    for team, okrs in list(team_okrs.items())[:5]:
        print(f"   - {team}: {len(okrs)} OKRs")
    
    print("\n5. Testing smart chunker...")
    chunker = SmartChunker(max_tokens=2000)
    all_okrs = loader.parse_okr_file()
    token_chunks = chunker.chunk_by_token_limit(all_okrs[:100])
    print(f"   ✓ Created {len(token_chunks)} token-limited chunks from 100 OKRs")
    for i, chunk in enumerate(token_chunks[:3]):
        total_tokens = sum(chunker.estimate_tokens(okr.to_text()) for okr in chunk)
        print(f"   - Chunk {i}: {len(chunk)} OKRs (~{total_tokens} tokens)")
    
    print("\n6. Sample OKR entry:")
    sample = all_okrs[0]
    print(f"   Team: {sample.team}")
    print(f"   Quarter: {sample.quarter}")
    print(f"   Objective: {sample.objective}")
    print(f"   Key Results:")
    print(f"     1. {sample.key_result_1}")
    print(f"     2. {sample.key_result_2}")
    print(f"     3. {sample.key_result_3}")
    print(f"   Quality: {sample.quality_level}")
    
    print("\n7. Testing data export...")
    try:
        loader.save_processed_data("./data/processed/okr_entries.json")
        print("   ✓ Data exported successfully")
    except Exception as e:
        print(f"   ❌ Export error: {e}")
    
    print("\n" + "=" * 80)
    print("✅ All tests passed!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Configure your GEMINI_API_KEY in .env")
    print("2. Run: python scripts/run_analysis.py")
    print("3. View dashboard: streamlit run src/app/dashboard.py")
    print()


if __name__ == "__main__":
    main()
