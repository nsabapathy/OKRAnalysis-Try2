# 📖 OKR Analysis System - Usage Guide

## Overview

This guide walks you through using the OKR Analysis System to extract insights from your 500 OKRs.

## System Capabilities

### What the System Does

1. **Theme Extraction**: Identifies recurring strategic themes across all OKRs
2. **Quality Assessment**: Scores each OKR on 5 dimensions with improvement suggestions
3. **Alignment Analysis**: Detects which teams are aligned and where gaps exist
4. **Semantic Search**: Find similar OKRs by meaning, not just keywords
5. **Visualization**: Interactive dashboard with charts and filters

### What You Get

- **15-20 Strategic Themes** with examples and counts
- **Quality Scores** for each OKR (0-10 scale)
- **Team Alignment Heatmap** showing collaboration patterns
- **Executive Summary** with key insights and recommendations
- **Searchable Database** of all OKRs with semantic search

## Step-by-Step Workflow

### Phase 1: Setup (One-Time)

#### 1.1 Install Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed:**
- Google Gemini API client
- ChromaDB vector database
- Streamlit web framework
- Plotly visualization library
- Sentence transformers for embeddings
- Supporting libraries (pandas, numpy, etc.)

**Time:** 2-3 minutes

#### 1.2 Get Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key

**Cost:** Free tier available (60 requests/minute)

#### 1.3 Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API key
# Change this line:
GEMINI_API_KEY=your_gemini_api_key_here

# To:
GEMINI_API_KEY=AIzaSy...your_actual_key
```

#### 1.4 Verify Setup

```bash
python scripts/test_loader.py
```

**Expected output:**
```
✓ Total OKRs: 498
✓ Unique teams: 4
✓ Created 4 chunks
✓ All tests passed!
```

### Phase 2: Run Analysis

#### 2.1 Execute Analysis Pipeline

```bash
python scripts/run_analysis.py
```

**What happens:**

```
Step 1: Load 498 OKRs from data file
Step 2: Split into 4 chunks (125, 125, 125, 123 OKRs)
Step 3: Store OKRs in SQLite database
Step 4: Initialize Gemini Flash 2.0
Step 5: Extract themes (parallel map-reduce)
  ├─ Process Chunk 0 → Extract themes
  ├─ Process Chunk 1 → Extract themes
  ├─ Process Chunk 2 → Extract themes
  └─ Process Chunk 3 → Extract themes
  └─ Reduce: Aggregate and deduplicate themes
Step 6: Assess quality (50 sample OKRs in parallel)
Step 7: Index OKRs in ChromaDB vector database
Step 8: Compute team alignment matrix
Step 9: Generate executive summary
```

**Runtime:** 3-5 minutes  
**API Cost:** ~$0.30  
**Output:** Results stored in `./data/`

#### 2.2 Monitor Progress

The script shows real-time progress:
- Progress bars for each step
- Chunk processing status
- API call timing
- Success/error messages

#### 2.3 Review Console Output

At the end, you'll see:
- Executive summary (AI-generated)
- Key statistics
- File locations
- Next steps

### Phase 3: Explore Dashboard

#### 3.1 Launch Dashboard

```bash
streamlit run src/app/dashboard.py
```

**Access:** http://localhost:8501

#### 3.2 Navigate Tabs

**📈 Overview Tab**
- View key metrics at a glance
- See quality distribution
- Explore top themes

**🎨 Theme Analysis Tab**
- Interactive sunburst chart
- Detailed theme table
- Click themes to see examples

**⭐ Quality Metrics Tab**
- Quality scores by team
- Radar chart of dimensions
- Top performers
- Areas needing improvement

**🔗 Alignment & Gaps Tab**
- Heatmap of team alignment
- Strongest alignments
- Weakest alignments
- Collaboration opportunities

**🔍 Search Tab**
- Enter natural language queries
- Filter by team
- Adjust number of results
- View similar OKRs

#### 3.3 Use Filters

**Sidebar Filters:**
- Select specific teams
- Filter by quarter
- View dataset info

**Filters apply to:**
- All visualizations
- Quality metrics
- Theme analysis

### Phase 4: Export Results

#### 4.1 Export to CSV/Excel

```bash
python scripts/export_results.py
```

**Exports:**
- `exports/okrs_[timestamp].csv` - All OKRs
- `exports/quality_scores_[timestamp].csv` - Quality assessments
- `exports/themes_[timestamp].csv` - Theme analysis
- `exports/alignment_matrix_[timestamp].csv` - Alignment scores

**Also creates Excel (.xlsx) versions**

#### 4.2 Access Raw Data

**JSON Files** (in `./data/processed/`):
- `themes.json` - Theme analysis
- `quality_scores.json` - Quality assessments
- `alignment.json` - Alignment matrix
- `executive_summary.txt` - AI summary
- `okr_entries.json` - Parsed OKRs

**SQLite Database:**
- `./data/okr_results.db` - All results in queryable format

**ChromaDB:**
- `./data/chroma_db/` - Vector embeddings for search

## Common Use Cases

### Use Case 1: Find Strategic Themes

**Goal:** Understand what the organization is focusing on

**Steps:**
1. Run analysis: `python scripts/run_analysis.py`
2. Open dashboard: `streamlit run src/app/dashboard.py`
3. Go to "Theme Analysis" tab
4. Review top themes in sunburst chart
5. Click themes to see examples

**Example Insights:**
- "Customer Experience" appears in 45 OKRs
- "Operational Efficiency" is a focus for Engineering and IT
- "Digital Transformation" spans multiple teams

### Use Case 2: Assess OKR Quality

**Goal:** Identify which OKRs need improvement

**Steps:**
1. Run analysis (if not already done)
2. Open dashboard
3. Go to "Quality Metrics" tab
4. Review quality distribution
5. Check "Needs Improvement" section
6. Read specific suggestions for each OKR

**Example Insights:**
- Average quality score: 7.2/10
- 15 OKRs need better measurability
- Top issue: Vague key results without metrics

### Use Case 3: Find Team Alignment

**Goal:** See which teams are aligned and where gaps exist

**Steps:**
1. Run analysis
2. Open dashboard
3. Go to "Alignment & Gaps" tab
4. Study the heatmap
5. Review strongest/weakest alignments

**Example Insights:**
- Engineering and IT are highly aligned (0.82)
- Sales and HR have low alignment (0.45)
- Opportunity: Sales and Marketing should collaborate more

### Use Case 4: Search for Similar OKRs

**Goal:** Find OKRs related to a specific topic

**Steps:**
1. Run analysis (to build vector index)
2. Open dashboard
3. Go to "Search" tab
4. Enter query (e.g., "improve customer satisfaction")
5. Review results

**Example Queries:**
- "reduce costs"
- "improve security"
- "enhance user experience"
- "increase revenue"
- "optimize performance"

### Use Case 5: Compare Teams

**Goal:** See which teams have the highest quality OKRs

**Steps:**
1. Run analysis
2. Open dashboard
3. Go to "Quality Metrics" tab
4. Review "Quality by Team" box plot
5. Check "Team Comparison" bar chart

**Example Insights:**
- Engineering has highest average quality (8.1/10)
- Sales needs improvement in measurability
- HR excels at clarity but needs more ambition

## Advanced Usage

### Customize Analysis

#### Adjust Sample Size

Edit `scripts/run_analysis.py`:

```python
# Line ~60: Change quality assessment sample size
sample_size = min(100, len(all_okrs))  # Increase from 50 to 100
```

#### Change Parallel Workers

Edit `.env`:

```bash
MAX_WORKERS=8  # Increase from 4 (if API rate limits allow)
```

#### Use Different Model

Edit `.env`:

```bash
GEMINI_MODEL=gemini-1.5-pro  # Higher quality, slower, more expensive
```

### Re-run Analysis

```bash
# Clean previous results
python scripts/clean_data.py

# Run fresh analysis
python scripts/run_analysis.py
```

### Query Database Directly

```python
import sqlite3

conn = sqlite3.connect('./data/okr_results.db')
cursor = conn.cursor()

# Get all high-quality OKRs
cursor.execute("""
    SELECT team, objective, overall_score 
    FROM quality_scores 
    WHERE overall_score >= 8
    ORDER BY overall_score DESC
""")

results = cursor.fetchall()
for team, objective, score in results:
    print(f"{team}: {objective} ({score:.1f})")
```

### Use Individual Modules

```python
from src.data.okr_loader import OKRTextLoader
from src.search.vector_search import OKRVectorSearch

# Load data
loader = OKRTextLoader("./data/okr_samples_500.txt")
okrs = loader.parse_okr_file()

# Search
search = OKRVectorSearch()
results = search.find_similar_okrs("improve customer experience", top_k=5)

for result in results:
    print(result['metadata']['objective'])
```

## Interpreting Results

### Theme Analysis

**What to look for:**
- Are themes aligned with company strategy?
- Are any critical areas missing?
- Are teams duplicating efforts?

**Action items:**
- Reinforce strategic themes in communications
- Address gaps in coverage
- Consolidate duplicate efforts

### Quality Scores

**Score Ranges:**
- **8-10**: Excellent OKRs, use as examples
- **6-8**: Good OKRs, minor improvements needed
- **<6**: Needs significant improvement

**Common Issues:**
- Vague objectives without clear outcomes
- Key results that aren't measurable
- Unrealistic or too-easy targets
- Misalignment with company goals

### Alignment Insights

**Alignment Score Ranges:**
- **0.7-1.0**: Strong alignment, good collaboration
- **0.5-0.7**: Moderate alignment, some synergy
- **<0.5**: Low alignment, potential gaps

**What to investigate:**
- Why are certain teams isolated?
- Are there opportunities for collaboration?
- Do conflicts need resolution?

## Troubleshooting

### Issue: API Key Error

**Error:** `GEMINI_API_KEY not found`

**Solution:**
1. Check `.env` file exists
2. Verify API key is correct
3. No quotes around the key
4. No spaces before/after `=`

### Issue: Import Errors

**Error:** `ModuleNotFoundError`

**Solution:**
```bash
# Make sure you're in project root
cd /path/to/OKRAnalysis-Try2

# Reinstall dependencies
pip install -r requirements.txt

# Run with full path
python scripts/run_analysis.py
```

### Issue: Slow Performance

**Symptoms:** Analysis takes > 10 minutes

**Solutions:**
1. Reduce workers: Set `MAX_WORKERS=2` in `.env`
2. Reduce sample: Edit `run_analysis.py`, set `sample_size = 25`
3. Check internet connection
4. Check Gemini API status

### Issue: ChromaDB Errors

**Error:** Database corruption or initialization errors

**Solution:**
```bash
# Delete vector database
rm -rf ./data/chroma_db

# Re-run analysis
python scripts/run_analysis.py
```

### Issue: Dashboard Not Loading

**Error:** Dashboard shows "No data found"

**Solution:**
1. Run analysis first: `python scripts/run_analysis.py`
2. Check database exists: `ls -la ./data/okr_results.db`
3. Verify data: `python scripts/test_loader.py`

## Performance Optimization

### For Faster Analysis

1. **Reduce sample size** (quality assessment)
2. **Increase workers** (if API allows)
3. **Use caching** (results are cached automatically)
4. **Skip vector indexing** (if you don't need search)

### For Better Quality

1. **Use gemini-1.5-pro** model
2. **Increase temperature** (0.5-0.7 for more creative analysis)
3. **Analyze all OKRs** (not just samples)
4. **Adjust prompts** in `src/utils/llm_client.py`

## Best Practices

### 1. Start Small
- Run with default settings first
- Validate results make sense
- Then scale up if needed

### 2. Review Prompts
- Check `src/utils/llm_client.py`
- Adjust prompts for your context
- Test with small samples first

### 3. Validate Results
- Manually review sample of results
- Compare with human expert assessment
- Iterate on prompts if needed

### 4. Use Caching
- Results are cached automatically
- Re-running is fast and free
- Clean cache only when needed

### 5. Export for Sharing
- Use export script for CSV/Excel
- Share dashboard URL (if deployed)
- Include executive summary

## Integration Examples

### Export to PowerPoint

```python
from pptx import Presentation
import pandas as pd

# Load themes
df = pd.read_csv('./exports/themes_latest.csv')

# Create presentation
prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = "OKR Theme Analysis"

# Add themes to slide
# ... (add your PowerPoint generation code)
```

### Email Summary

```python
import smtplib
from email.mime.text import MIMEText

# Load executive summary
with open('./data/processed/executive_summary.txt', 'r') as f:
    summary = f.read()

# Send email
# ... (add your email code)
```

### Slack Integration

```python
import requests

# Load top themes
with open('./data/processed/themes.json', 'r') as f:
    themes = json.load(f)

top_themes = themes['themes'][:5]

message = "🎯 Weekly OKR Analysis:\n\n"
for theme in top_themes:
    message += f"• {theme['name']}: {theme['count']} OKRs\n"

# Post to Slack
# ... (add your Slack webhook code)
```

## Maintenance

### Regular Tasks

**Weekly:**
- Re-run analysis if OKRs change
- Review dashboard for new insights
- Export results for stakeholders

**Monthly:**
- Clean old cache: `python scripts/clean_data.py`
- Update dependencies: `pip install -r requirements.txt --upgrade`
- Review and adjust prompts

**Quarterly:**
- Validate accuracy against human reviews
- Analyze trends across quarters
- Update documentation

### Backup

```bash
# Backup database
cp ./data/okr_results.db ./backups/okr_results_$(date +%Y%m%d).db

# Backup vector database
tar -czf ./backups/chroma_db_$(date +%Y%m%d).tar.gz ./data/chroma_db/

# Backup results
tar -czf ./backups/processed_$(date +%Y%m%d).tar.gz ./data/processed/
```

## FAQ

**Q: How accurate is the analysis?**  
A: Gemini Flash 2.0 provides high-quality analysis. We recommend validating a sample against human expert reviews.

**Q: Can I analyze more than 500 OKRs?**  
A: Yes! The system scales to thousands of OKRs. Just update the data file and adjust chunk sizes.

**Q: How much does it cost?**  
A: For 500 OKRs: ~$0.30 per run. Subsequent runs use caching and cost less.

**Q: Can I use my own LLM?**  
A: Yes! Edit `src/utils/llm_client.py` to use Azure OpenAI, Anthropic, or local models.

**Q: How do I share results?**  
A: Use the export script to create CSV/Excel files, or deploy the dashboard to a server.

**Q: Can I customize the analysis?**  
A: Yes! Edit prompts in `src/utils/llm_client.py` and adjust parameters in `.env`.

**Q: What if analysis fails?**  
A: Check API key, internet connection, and rate limits. Results are cached, so you can resume.

**Q: How do I update the OKR data?**  
A: Replace `./data/okr_samples_500.txt` with your new data, then re-run analysis.

## Getting Help

1. **Check documentation:**
   - `README.md` - Overview and features
   - `QUICKSTART.md` - 5-minute setup
   - `IMPLEMENTATION_SUMMARY.md` - Technical details

2. **Test components:**
   - `python scripts/test_loader.py` - Test data loading
   - `pytest tests/` - Run unit tests

3. **Review logs:**
   - Console output from analysis script
   - Streamlit logs in terminal

4. **Check configuration:**
   - Verify `.env` settings
   - Validate API key
   - Check file paths

---

**Ready to analyze!** 🚀

Start with: `python scripts/run_analysis.py`
