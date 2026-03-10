# 🎯 OKR Analysis System

AI-powered OKR (Objectives and Key Results) analysis system supporting multiple LLM providers (Google Gemini and Qwen) with ChromaDB for theme extraction, quality assessment, and alignment analysis.

## Features

- **Theme Extraction**: Identify recurring strategic themes across all OKRs using LLM-based analysis
- **Quality Assessment**: Score OKRs on clarity, measurability, ambition, alignment, and actionability
- **Alignment Analysis**: Detect cross-team alignment and collaboration opportunities
- **Semantic Search**: Find similar OKRs using vector embeddings
- **Interactive Dashboard**: Explore insights through a modern Streamlit web interface
- **Parallel Processing**: Process large datasets efficiently with map-reduce pattern

## Architecture

```
┌─────────────────┐
│  OKR Text File  │
│   (500 OKRs)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Loader    │
│  (4 chunks)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Parallel Processing (Map)      │
│  ┌──────┐ ┌──────┐ ┌──────┐    │
│  │Chunk1│ │Chunk2│ │Chunk3│ ...│
│  └──┬───┘ └──┬───┘ └──┬───┘    │
└─────┼────────┼────────┼─────────┘
      │        │        │
      ▼        ▼        ▼
┌─────────────────────────────────┐
│   Gemini Flash 2.0 API          │
│   (Theme & Quality Analysis)    │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Reduce Phase   │
│  (Aggregate)    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Storage Layer                  │
│  ├─ SQLite (Results)            │
│  ├─ ChromaDB (Vectors)          │
│  └─ JSON (Cache)                │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Streamlit      │
│  Dashboard      │
└─────────────────┘
```

## Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- LLM API key:
  - **Google Gemini**: [Get API key here](https://makersuite.google.com/app/apikey)
  - **Qwen**: [Get API key here](https://dashscope.aliyun.com/)

### 2. Installation

```bash
# Clone or navigate to the project directory
cd OKRAnalysis-Try2

# Run setup script
python scripts/setup.py

# This will:
# - Check Python version
# - Install dependencies
# - Create .env file
```

### 3. Configuration

Edit `.env` file and configure your LLM provider:

**Option A: Using Google Gemini (default)**

```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite
```

**Option B: Using Qwen**

```bash
LLM_PROVIDER=qwen
QWEN_API_KEY=your_qwen_api_key_here
QWEN_MODEL=qwen-plus
```

### 4. Run Analysis

```bash
# Run the complete analysis pipeline
python scripts/run_analysis.py

# This will:
# - Load 500 OKRs from data/okr_samples_500.txt
# - Split into 4 chunks for parallel processing
# - Extract themes using map-reduce
# - Assess quality (sample of 50 OKRs)
# - Compute team alignment
# - Generate executive summary
# - Store results in SQLite and ChromaDB
```

### 5. View Dashboard

```bash
# Launch the interactive dashboard
streamlit run src/app/dashboard.py

# Dashboard will open at http://localhost:8501
```

## Dashboard Features

### 📈 Overview Tab
- Key metrics: Total OKRs, teams, average quality score, themes identified
- Quality distribution histogram
- Top themes bar chart

### 🎨 Theme Analysis Tab
- Interactive sunburst chart of theme distribution
- Detailed theme table with descriptions and counts
- Example objectives for each theme

### ⭐ Quality Metrics Tab
- Quality score distribution by team (box plots)
- Radar chart of quality dimensions
- Team comparison across all dimensions
- Top quality OKRs showcase
- OKRs needing improvement with suggestions

### 🔍 Search Tab
- Semantic search across all OKRs
- Filter by team and quarter
- Find similar OKRs by meaning, not just keywords

## Project Structure

```
OKRAnalysis-Try2/
├── src/
│   ├── data/
│   │   └── okr_loader.py          # Data loading and chunking
│   ├── analysis/
│   │   ├── llm_analyzer.py        # Core LLM analysis engine
│   │   ├── theme_extractor.py     # Theme extraction
│   │   ├── quality_scorer.py      # Quality assessment
│   │   └── alignment_detector.py  # Alignment analysis
│   ├── search/
│   │   └── vector_search.py       # ChromaDB vector search
│   ├── app/
│   │   ├── dashboard.py           # Main Streamlit app
│   │   └── components/
│   │       └── charts.py          # Visualization components
│   └── utils/
│       ├── llm_client.py          # LLM abstraction layer
│       └── storage.py             # SQLite storage
├── data/
│   ├── okr_samples_500.txt        # Input OKR data (500 entries)
│   ├── processed/                 # Analysis results (JSON)
│   ├── chroma_db/                 # Vector database
│   └── okr_results.db             # SQLite database
├── scripts/
│   ├── setup.py                   # Setup and validation
│   └── run_analysis.py            # Main analysis script
├── requirements.txt
├── .env.example
└── README.md
```

## Configuration

Edit `.env` to customize settings:

```bash
# LLM Provider Selection
LLM_PROVIDER=gemini                # Options: gemini, qwen

# Google Gemini Configuration
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite

# Qwen Configuration
QWEN_API_KEY=your_qwen_api_key_here
QWEN_MODEL=qwen-plus               # Options: qwen-plus, qwen-turbo, qwen-max

# Processing Settings
CHUNK_SIZE=125                     # OKRs per chunk
MAX_WORKERS=4                      # Parallel workers

# Embedding Model
EMBEDDING_MODEL=intfloat/multilingual-e5-large

# LLM Settings
TEMPERATURE=0.3
MAX_TOKENS=8000
```

## Cost Estimates

**Using Gemini Flash 2.5 Lite:**
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens
- **For 500 OKRs**: ~$0.30 per run
- **For 10,000 OKRs**: ~$5-10 per complete analysis

**Using Qwen:**
- Qwen-Plus: ¥0.004 per 1K tokens (~$0.0006 USD)
- Qwen-Turbo: ¥0.002 per 1K tokens (~$0.0003 USD)
- **For 500 OKRs**: ~$0.05-0.10 per run
- **For 10,000 OKRs**: ~$1-2 per complete analysis

## Performance

**Expected runtime for 500 OKRs:**
- Data loading: < 5 seconds
- Theme extraction (4 parallel chunks): 30-60 seconds
- Quality assessment (50 samples): 60-90 seconds
- Vector indexing: 30-60 seconds
- Alignment computation: 20-40 seconds
- **Total**: 3-5 minutes

## Usage Examples

### Run Full Analysis

```bash
python scripts/run_analysis.py
```

### Launch Dashboard

```bash
streamlit run src/app/dashboard.py
```

### Use Individual Modules

```python
from src.data.okr_loader import OKRTextLoader
from src.analysis.llm_analyzer import OKRAnalyzer

# Load data
loader = OKRTextLoader("./data/okr_samples_500.txt")
okrs = loader.parse_okr_file()

# Analyze
analyzer = OKRAnalyzer()
chunks = loader.chunk_for_parallel_processing(num_chunks=4)
themes = analyzer.extract_themes_parallel(chunks, max_workers=4)

print(f"Found {len(themes['themes'])} themes")
```

## Troubleshooting

### "API_KEY not found"
- Make sure `.env` file exists and contains your API key
- For Gemini: Check that the key is valid at https://makersuite.google.com/
- For Qwen: Check that the key is valid at https://dashscope.aliyun.com/
- Verify `LLM_PROVIDER` is set correctly in `.env`

### "Module not found" errors
- Run: `pip install -r requirements.txt`
- Make sure you're in the project root directory
- For Qwen support, ensure `openai` package is installed

### Slow performance
- Reduce `MAX_WORKERS` in `.env` (try 2 instead of 4)
- Reduce sample size in `run_analysis.py`
- Check your internet connection (API calls require network)
- Try switching providers: Qwen is often faster than Gemini

### ChromaDB errors
- Delete `./data/chroma_db/` folder and re-run
- Make sure you have enough disk space (needs ~500MB)

### Switching between providers
- Update `LLM_PROVIDER` in `.env` to either `gemini` or `qwen`
- Make sure the corresponding API key is set
- No code changes needed - the system handles provider switching automatically

## Development

### Run Tests

```bash
pytest tests/
```

### Add New Analysis Module

1. Create module in `src/analysis/`
2. Import in `scripts/run_analysis.py`
3. Add results to storage
4. Update dashboard to display results

## Migration to Azure

This prototype is designed for easy migration to Azure:

- **LLM**: Swap `google.generativeai` → `openai` (Azure OpenAI)
- **Vector DB**: Export ChromaDB → Azure AI Search
- **Storage**: Migrate SQLite → Azure Cosmos DB
- **Hosting**: Deploy Streamlit → Azure Container Apps

See `OKR_Analysis_Architecture_Plan.md` for detailed migration guide.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the architecture plan document
3. Check API quotas and rate limits

## License

Internal use only.
