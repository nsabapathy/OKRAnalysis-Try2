#!/usr/bin/env python3
"""
Main Analysis Script
Orchestrates the complete OKR analysis pipeline with parallel processing
"""

import sys
from pathlib import Path
import time
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.okr_loader import OKRTextLoader
from src.analysis.llm_analyzer import OKRAnalyzer
from src.analysis.theme_extractor import ThemeExtractor
from src.analysis.quality_scorer import QualityScorer
from src.analysis.alignment_detector import AlignmentDetector
from src.search.vector_search import OKRVectorSearch
from src.utils.storage import ResultsStorage
from src.utils.config import Config


def print_banner():
    """Print welcome banner"""
    print("=" * 80)
    print("🎯 OKR ANALYSIS SYSTEM")
    print("=" * 80)
    print(f"Analysis started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    Config.print_config()
    print("=" * 80)
    print()


def main():
    print_banner()
    
    if not Config.validate():
        print("\n❌ Configuration validation failed. Please check your .env file.")
        sys.exit(1)
    
    print("📁 Step 1: Loading OKR data...")
    loader = OKRTextLoader(Config.OKR_DATA_PATH)
    
    stats = loader.get_statistics()
    print(f"   ✓ Loaded {stats['total_entries']} OKR entries")
    print(f"   ✓ Teams: {stats['unique_teams']}")
    print(f"   ✓ Quarters: {stats['unique_quarters']}")
    print(f"   ✓ Quality distribution: {stats['quality_distribution']}")
    print()
    
    print("📦 Step 2: Chunking data for parallel processing...")
    chunks = loader.chunk_for_parallel_processing(num_chunks=4)
    print(f"   ✓ Created {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        print(f"   - Chunk {i}: {len(chunk)} OKRs")
    print()
    
    print("💾 Step 3: Storing OKRs in database...")
    storage = ResultsStorage()
    all_okrs = loader.parse_okr_file()
    storage.store_okrs([okr.to_dict() for okr in all_okrs])
    print()
    
    print("🧠 Step 4: Initializing LLM analyzer...")
    if Config.LLM_PROVIDER == "gemini":
        analyzer = OKRAnalyzer(api_key=Config.GEMINI_API_KEY, model_name=Config.GEMINI_MODEL, provider="gemini")
        print(f"   ✓ {Config.GEMINI_MODEL} initialized")
    elif Config.LLM_PROVIDER == "qwen":
        analyzer = OKRAnalyzer(api_key=Config.QWEN_API_KEY, model_name=Config.QWEN_MODEL, provider="qwen")
        print(f"   ✓ {Config.QWEN_MODEL} initialized")
    print()
    
    print("🎨 Step 5: Extracting themes (parallel map-reduce)...")
    theme_extractor = ThemeExtractor(analyzer)
    start_time = time.time()
    theme_results = theme_extractor.extract_themes_from_chunks(chunks, max_workers=Config.MAX_WORKERS)
    elapsed = time.time() - start_time
    
    print(f"   ✓ Theme extraction completed in {elapsed:.1f} seconds")
    print(f"   ✓ Identified {len(theme_results.get('themes', []))} themes")
    
    if theme_results.get('themes'):
        print("\n   Top 5 Themes:")
        for i, theme in enumerate(theme_results['themes'][:5], 1):
            print(f"   {i}. {theme['name']} ({theme.get('count', 0)} OKRs)")
    
    storage.store_themes(theme_results.get('themes', []))
    theme_extractor.save_themes(theme_results, "./data/processed/themes.json")
    print()
    
    print("⭐ Step 6: Assessing OKR quality (sampling for prototype)...")
    quality_scorer = QualityScorer(analyzer)
    
    sample_size = min(50, len(all_okrs))
    sample_okrs = all_okrs[:sample_size]
    print(f"   ℹ️  Analyzing sample of {sample_size} OKRs (to save time/cost)")
    print(f"   ℹ️  For full analysis, remove sampling in the script")
    
    start_time = time.time()
    quality_results = quality_scorer.score_okrs(sample_okrs, max_workers=Config.MAX_WORKERS)
    elapsed = time.time() - start_time
    
    print(f"   ✓ Quality assessment completed in {elapsed:.1f} seconds")
    
    quality_stats = quality_scorer.get_quality_statistics(quality_results)
    if 'overall' in quality_stats:
        print(f"   ✓ Average quality score: {quality_stats['overall']['mean']:.1f}/10")
        print(f"   ✓ High quality OKRs (8+): {quality_stats['distribution']['high_quality_8_plus']}")
        print(f"   ✓ Needs improvement (<6): {quality_stats['distribution']['needs_improvement_below_6']}")
    
    storage.store_quality_scores(quality_results)
    quality_scorer.save_quality_results(quality_results, "./data/processed/quality_scores.json")
    print()
    
    print("🔍 Step 7: Indexing OKRs in vector database...")
    vector_search = OKRVectorSearch(persist_directory=Config.CHROMA_DB_PATH)
    
    existing_count = vector_search.collection.count()
    if existing_count > 0:
        print(f"   ℹ️  Vector database already contains {existing_count} OKRs")
        print(f"   ℹ️  Skipping indexing (delete ./data/chroma_db to re-index)")
    else:
        start_time = time.time()
        vector_search.index_okrs_batch(all_okrs, batch_size=100)
        elapsed = time.time() - start_time
        print(f"   ✓ Indexing completed in {elapsed:.1f} seconds")
    
    print()
    
    print("🔗 Step 8: Computing team alignment...")
    alignment_detector = AlignmentDetector(analyzer, vector_search)
    
    team_okrs = loader.chunk_by_team()
    teams = list(team_okrs.keys())
    
    print(f"   ℹ️  Computing alignment for {len(teams)} teams...")
    alignment_matrix = alignment_detector.compute_alignment_matrix(teams)
    
    print(f"   ✓ Average alignment score: {alignment_matrix['average_alignment']:.2f}")
    
    storage.store_alignment_scores(alignment_matrix['pairwise_alignments'])
    alignment_detector.save_alignment_results(alignment_matrix, "./data/processed/alignment.json")
    
    isolated_teams = alignment_detector.find_isolated_teams(alignment_matrix, threshold=0.5)
    if isolated_teams:
        print(f"   ⚠️  Teams with low alignment: {', '.join(isolated_teams)}")
    print()
    
    print("📊 Step 9: Generating executive summary...")
    
    llm_alignment_results = analyzer.analyze_team_alignment(team_okrs)
    
    summary = analyzer.generate_summary_report(
        theme_results,
        quality_results,
        llm_alignment_results
    )
    
    summary_path = "./data/processed/executive_summary.txt"
    Path(summary_path).parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print("   ✓ Executive summary generated")
    print()
    print("=" * 80)
    print("EXECUTIVE SUMMARY")
    print("=" * 80)
    print(summary)
    print("=" * 80)
    print()
    
    avg_quality = quality_stats['overall']['mean'] if 'overall' in quality_stats else 0
    storage.record_analysis_run(
        total_okrs=len(all_okrs),
        total_themes=len(theme_results.get('themes', [])),
        avg_quality=avg_quality,
        status="completed"
    )
    
    print("✅ Analysis complete!")
    print()
    print("📊 To view the dashboard, run:")
    print("   streamlit run src/app/dashboard.py")
    print()
    print("📁 Results saved to:")
    print(f"   - Database: ./data/okr_results.db")
    print(f"   - Themes: ./data/processed/themes.json")
    print(f"   - Quality: ./data/processed/quality_scores.json")
    print(f"   - Alignment: ./data/processed/alignment.json")
    print(f"   - Summary: ./data/processed/executive_summary.txt")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
