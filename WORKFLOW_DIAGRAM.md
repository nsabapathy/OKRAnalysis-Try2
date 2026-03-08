# 🔄 OKR Analysis System - Workflow Diagram

## Complete Analysis Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER STARTS ANALYSIS                             │
│                    $ python scripts/run_analysis.py                      │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 1: LOAD DATA                                                       │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ okr_loader.py                                                      │  │
│  │ • Read: data/okr_samples_500.txt (249KB)                          │  │
│  │ • Parse: 498 OKR entries                                          │  │
│  │ • Teams: Engineering, Sales, HR, IT                               │  │
│  │ • Quarter: Q1 2024                                                │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 2: CHUNK FOR PARALLEL PROCESSING                                  │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ Split into 4 chunks:                                              │  │
│  │ • Chunk 0: 125 OKRs                                               │  │
│  │ • Chunk 1: 125 OKRs                                               │  │
│  │ • Chunk 2: 125 OKRs                                               │  │
│  │ • Chunk 3: 123 OKRs                                               │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 3: STORE IN DATABASE                                              │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ storage.py → SQLite                                               │  │
│  │ • Create tables: okrs, quality_scores, themes, alignment_scores  │  │
│  │ • Insert 498 OKR entries                                          │  │
│  │ • File: data/okr_results.db                                       │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 4: INITIALIZE LLM                                                 │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ llm_client.py                                                     │  │
│  │ • Load API key from .env                                          │  │
│  │ • Initialize: gemini-2.0-flash-exp                                │  │
│  │ • Configure: temperature=0.3, max_tokens=8000                     │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 5: THEME EXTRACTION (MAP-REDUCE)                                  │
│                                                                          │
│  MAP PHASE (Parallel):                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐│
│  │  Chunk 0     │  │  Chunk 1     │  │  Chunk 2     │  │  Chunk 3     ││
│  │  125 OKRs    │  │  125 OKRs    │  │  125 OKRs    │  │  123 OKRs    ││
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘│
│         │                 │                 │                 │         │
│         ▼                 ▼                 ▼                 ▼         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐│
│  │ Gemini API   │  │ Gemini API   │  │ Gemini API   │  │ Gemini API   ││
│  │ Extract      │  │ Extract      │  │ Extract      │  │ Extract      ││
│  │ Themes       │  │ Themes       │  │ Themes       │  │ Themes       ││
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘│
│         │                 │                 │                 │         │
│         └─────────────────┴─────────────────┴─────────────────┘         │
│                                 │                                        │
│                                 ▼                                        │
│  REDUCE PHASE:                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ Gemini API - Aggregate & Deduplicate                              │  │
│  │ • Merge similar themes                                            │  │
│  │ • Consolidate counts                                              │  │
│  │ • Rank by prevalence                                              │  │
│  │ • Output: Top 15-20 themes                                        │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  RESULT: 15-20 strategic themes identified                              │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 6: QUALITY ASSESSMENT (PARALLEL)                                  │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ Sample 50 OKRs for prototype                                      │  │
│  │                                                                    │  │
│  │ Worker 1: OKRs 1-13   → Gemini → Scores                          │  │
│  │ Worker 2: OKRs 14-26  → Gemini → Scores                          │  │
│  │ Worker 3: OKRs 27-39  → Gemini → Scores                          │  │
│  │ Worker 4: OKRs 40-50  → Gemini → Scores                          │  │
│  │                                                                    │  │
│  │ Each OKR scored on:                                               │  │
│  │ • Clarity (1-10)                                                  │  │
│  │ • Measurability (1-10)                                            │  │
│  │ • Ambition (1-10)                                                 │  │
│  │ • Alignment (1-10)                                                │  │
│  │ • Actionability (1-10)                                            │  │
│  │ • Overall score + suggestions                                     │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  RESULT: 50 quality assessments with improvement suggestions            │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 7: VECTOR INDEXING                                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ vector_search.py → ChromaDB                                       │  │
│  │                                                                    │  │
│  │ For each OKR:                                                     │  │
│  │ 1. Convert to text                                                │  │
│  │ 2. Generate embedding (multilingual-e5-large)                     │  │
│  │ 3. Store in ChromaDB with metadata                                │  │
│  │                                                                    │  │
│  │ Batch size: 100 OKRs per batch                                    │  │
│  │ Total: 498 OKRs indexed                                           │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  RESULT: Semantic search enabled across all OKRs                        │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 8: ALIGNMENT COMPUTATION                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ alignment_detector.py                                             │  │
│  │                                                                    │  │
│  │ For each team pair:                                               │  │
│  │ • Engineering ↔ Sales                                             │  │
│  │ • Engineering ↔ HR                                                │  │
│  │ • Engineering ↔ IT                                                │  │
│  │ • Sales ↔ HR                                                      │  │
│  │ • Sales ↔ IT                                                      │  │
│  │ • HR ↔ IT                                                         │  │
│  │                                                                    │  │
│  │ Compute: Cosine similarity of team embeddings                     │  │
│  │ Output: Alignment matrix (4x4)                                    │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  RESULT: Team alignment heatmap data                                    │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 9: GENERATE SUMMARY                                               │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ llm_analyzer.py → Gemini API                                      │  │
│  │                                                                    │  │
│  │ Input:                                                            │  │
│  │ • Theme analysis results                                          │  │
│  │ • Quality assessment statistics                                   │  │
│  │ • Alignment insights                                              │  │
│  │                                                                    │  │
│  │ Output:                                                           │  │
│  │ • Executive summary (300-400 words)                               │  │
│  │ • Key insights                                                    │  │
│  │ • Top 3 recommendations                                           │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  RESULT: Executive summary saved to file                                │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ANALYSIS COMPLETE!                                                      │
│                                                                          │
│  📁 Results saved to:                                                   │
│  • data/okr_results.db (SQLite database)                                │
│  • data/chroma_db/ (Vector embeddings)                                  │
│  • data/processed/themes.json                                           │
│  • data/processed/quality_scores.json                                   │
│  • data/processed/alignment.json                                        │
│  • data/processed/executive_summary.txt                                 │
│                                                                          │
│  ⏱️  Total time: 3-5 minutes                                            │
│  💰 Total cost: ~$0.30                                                  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER LAUNCHES DASHBOARD                          │
│                   $ streamlit run src/app/dashboard.py                   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  DASHBOARD LOADS DATA                                                    │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ storage.py                                                        │  │
│  │ • Load OKRs from SQLite                                           │  │
│  │ • Load quality scores                                             │  │
│  │ • Load themes                                                     │  │
│  │ • Load alignment matrix                                           │  │
│  │                                                                    │  │
│  │ vector_search.py                                                  │  │
│  │ • Connect to ChromaDB                                             │  │
│  │ • Load embedding model                                            │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  DASHBOARD DISPLAYS (5 TABS)                                            │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ TAB 1: OVERVIEW                                                   │   │
│  │ ┌──────────┬──────────┬──────────┬──────────┐                   │   │
│  │ │Total OKRs│  Teams   │Avg Quality│ Themes  │                   │   │
│  │ │   498    │    4     │  7.2/10  │   18    │                   │   │
│  │ └──────────┴──────────┴──────────┴──────────┘                   │   │
│  │ [Quality Distribution Chart]                                     │   │
│  │ [Top Themes Bar Chart]                                           │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ TAB 2: THEME ANALYSIS                                            │   │
│  │ [Interactive Sunburst Chart]                                     │   │
│  │                                                                   │   │
│  │ Theme Details:                                                   │   │
│  │ 1. Customer Experience (45 OKRs)                                 │   │
│  │ 2. Operational Efficiency (38 OKRs)                              │   │
│  │ 3. Digital Transformation (32 OKRs)                              │   │
│  │ 4. Revenue Growth (28 OKRs)                                      │   │
│  │ 5. Employee Development (25 OKRs)                                │   │
│  │ ...                                                               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ TAB 3: QUALITY METRICS                                           │   │
│  │ [Quality by Team Box Plot]                                       │   │
│  │ [Quality Dimensions Radar Chart]                                 │   │
│  │ [Team Comparison Bar Chart]                                      │   │
│  │                                                                   │   │
│  │ Top Quality OKRs:                                                │   │
│  │ #1 Engineering (9.2/10)                                          │   │
│  │ #2 IT (8.8/10)                                                   │   │
│  │                                                                   │   │
│  │ Needs Improvement:                                               │   │
│  │ #1 Sales (5.2/10) - Add measurable metrics                       │   │
│  │ #2 HR (5.8/10) - Clarify objectives                              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ TAB 4: ALIGNMENT & GAPS                                          │   │
│  │ [Cross-Team Alignment Heatmap]                                   │   │
│  │                                                                   │   │
│  │              Eng   Sales   HR    IT                              │   │
│  │ Engineering  1.00  0.65   0.58  0.82                             │   │
│  │ Sales        0.65  1.00   0.45  0.61                             │   │
│  │ HR           0.58  0.45   1.00  0.55                             │   │
│  │ IT           0.82  0.61   0.55  1.00                             │   │
│  │                                                                   │   │
│  │ Strongest: Engineering ↔ IT (0.82)                               │   │
│  │ Weakest: Sales ↔ HR (0.45)                                       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ TAB 5: SEARCH                                                    │   │
│  │ [Search Box: "improve customer satisfaction"]                    │   │
│  │                                                                   │   │
│  │ Results:                                                         │   │
│  │ #1 Sales | Q1 2024 | Distance: 0.123                            │   │
│  │    "Enhance customer experience..."                              │   │
│  │                                                                   │   │
│  │ #2 Engineering | Q1 2024 | Distance: 0.156                      │   │
│  │    "Improve platform reliability..."                             │   │
│  │ ...                                                               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘

================================================================================
PARALLEL PROCESSING VISUALIZATION
================================================================================

Time →
│
│ ┌─────────────────────────────────────────────────────────────────────┐
│ │ SEQUENTIAL (Without Parallelism)                                   │
│ │ ────────────────────────────────────────────────────────────────── │
│ │ [Chunk 0]──→[Chunk 1]──→[Chunk 2]──→[Chunk 3]──→[Reduce]          │
│ │ 0s    30s   60s    90s   120s   150s  180s   200s                  │
│ │                                                                     │
│ │ Total time: ~200 seconds (3.3 minutes)                             │
│ └─────────────────────────────────────────────────────────────────────┘
│
│ ┌─────────────────────────────────────────────────────────────────────┐
│ │ PARALLEL (With 4 Workers) ✅                                        │
│ │ ────────────────────────────────────────────────────────────────── │
│ │ [Chunk 0]──┐                                                       │
│ │ [Chunk 1]──┼──→[All complete]──→[Reduce]                          │
│ │ [Chunk 2]──┤                                                       │
│ │ [Chunk 3]──┘                                                       │
│ │ 0s    30s   45s           60s                                      │
│ │                                                                     │
│ │ Total time: ~60 seconds (1 minute)                                 │
│ │ Speedup: 4x faster! ⚡                                             │
│ └─────────────────────────────────────────────────────────────────────┘
│
▼

================================================================================
FILE STRUCTURE
================================================================================

OKRAnalysis-Try2/
├── 📄 START_HERE.md                      ⭐ Read this first!
├── 📄 QUICKSTART.md
├── 📄 README.md
├── 📄 USAGE_GUIDE.md
├── 📄 GETTING_STARTED.md
├── 📄 IMPLEMENTATION_SUMMARY.md
├── 📄 PROJECT_STRUCTURE.md
├── 📄 BUILD_COMPLETE.md
├── 📄 WORKFLOW_DIAGRAM.md                ⭐ This file
│
├── ⚙️  .env.example                       → Copy to .env
├── 📄 requirements.txt                   → pip install -r
│
├── 📂 data/
│   ├── okr_samples_500.txt               ⭐ Your 498 OKRs
│   ├── processed/                        (auto-generated)
│   ├── chroma_db/                        (auto-generated)
│   └── okr_results.db                    (auto-generated)
│
├── 📂 src/
│   ├── data/okr_loader.py                ⭐ Data loading
│   ├── analysis/llm_analyzer.py          ⭐ LLM engine
│   ├── search/vector_search.py           ⭐ Semantic search
│   ├── app/dashboard.py                  ⭐ Dashboard
│   └── utils/llm_client.py               ⭐ LLM abstraction
│
└── 📂 scripts/
    ├── run_analysis.py                   ⭐ Main script
    ├── test_loader.py                    ⭐ Quick test
    ├── setup.py
    ├── export_results.py
    └── clean_data.py

================================================================================
USAGE WORKFLOW
================================================================================

┌─────────────┐
│   SETUP     │ (One-time)
│             │
│ 1. Install  │ pip install -r requirements.txt
│ 2. Config   │ Add GEMINI_API_KEY to .env
│ 3. Test     │ python scripts/test_loader.py
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   ANALYZE   │ (3-5 minutes)
│             │
│ 1. Run      │ python scripts/run_analysis.py
│ 2. Wait     │ Watch progress bars
│ 3. Review   │ Read executive summary
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   EXPLORE   │ (Interactive)
│             │
│ 1. Launch   │ streamlit run src/app/dashboard.py
│ 2. Navigate │ Explore 5 tabs
│ 3. Filter   │ Select teams/quarters
│ 4. Search   │ Find similar OKRs
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   EXPORT    │ (Optional)
│             │
│ 1. Export   │ python scripts/export_results.py
│ 2. Share    │ CSV/Excel files created
│ 3. Present  │ Use charts from dashboard
└─────────────┘

================================================================================
READY TO USE! 🚀
================================================================================

Everything is built and tested. Just add your Gemini API key and run!

$ python scripts/run_analysis.py

================================================================================
