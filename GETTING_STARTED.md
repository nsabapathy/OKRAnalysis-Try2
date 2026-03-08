# ✅ Getting Started Checklist

Follow this checklist to get your OKR Analysis System up and running.

## Pre-Flight Checklist

### ☐ Step 1: Verify Python Version

```bash
python --version
```

**Required:** Python 3.10 or higher

**If needed:**
```bash
# macOS
brew install python@3.10

# Or use pyenv
pyenv install 3.10.0
pyenv local 3.10.0
```

---

### ☐ Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed google-generativeai-0.8.0 chromadb-0.4.22 streamlit-1.30.0 ...
```

**Time:** 2-3 minutes

**Troubleshooting:**
- If errors occur, try: `pip install --upgrade pip`
- Use virtual environment: `python -m venv venv && source venv/bin/activate`

---

### ☐ Step 3: Get Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIzaSy...`)

**Cost:** Free tier includes 60 requests/minute

---

### ☐ Step 4: Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

**Update this line:**
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

**To:**
```bash
GEMINI_API_KEY=AIzaSy...your_actual_key
```

**Save and close**

---

### ☐ Step 5: Test Data Loading

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

**If this works, you're ready to proceed!**

---

## Launch Checklist

### ☐ Step 6: Run Analysis

```bash
python scripts/run_analysis.py
```

**What to expect:**

```
🎯 OKR ANALYSIS SYSTEM
================================================================================
Analysis started at: 2026-03-07 21:30:00
Configuration:
  Model: gemini-2.0-flash-exp
  Chunks: 125 OKRs per chunk
  Workers: 4 parallel workers
================================================================================

📁 Step 1: Loading OKR data...
   ✓ Loaded 498 OKR entries
   ✓ Teams: 4
   ✓ Quarters: 1

📦 Step 2: Chunking data for parallel processing...
   ✓ Created 4 chunks
   - Chunk 0: 125 OKRs
   - Chunk 1: 125 OKRs
   - Chunk 2: 125 OKRs
   - Chunk 3: 123 OKRs

💾 Step 3: Storing OKRs in database...
   ✓ Stored 498 OKRs

🧠 Step 4: Initializing LLM analyzer...
   ✓ gemini-2.0-flash-exp initialized

🎨 Step 5: Extracting themes (parallel map-reduce)...
Processing chunks: 100%|████████████| 4/4
   ✓ Theme extraction completed in 45.2 seconds
   ✓ Identified 18 themes

   Top 5 Themes:
   1. Customer Experience (45 OKRs)
   2. Operational Efficiency (38 OKRs)
   3. Digital Transformation (32 OKRs)
   4. Revenue Growth (28 OKRs)
   5. Employee Development (25 OKRs)

⭐ Step 6: Assessing OKR quality (sampling for prototype)...
   ℹ️  Analyzing sample of 50 OKRs
Quality assessment: 100%|████████████| 50/50
   ✓ Quality assessment completed in 78.5 seconds
   ✓ Average quality score: 7.2/10
   ✓ High quality OKRs (8+): 18
   ✓ Needs improvement (<6): 8

🔍 Step 7: Indexing OKRs in vector database...
Indexing OKRs: 100%|████████████| 5/5
   ✓ Indexing completed in 42.3 seconds

🔗 Step 8: Computing team alignment...
   ✓ Average alignment score: 0.64

📊 Step 9: Generating executive summary...
   ✓ Executive summary generated

================================================================================
EXECUTIVE SUMMARY
================================================================================
[AI-generated summary will appear here]
================================================================================

✅ Analysis complete!

📊 To view the dashboard, run:
   streamlit run src/app/dashboard.py

📁 Results saved to:
   - Database: ./data/okr_results.db
   - Themes: ./data/processed/themes.json
   - Quality: ./data/processed/quality_scores.json
   - Alignment: ./data/processed/alignment.json
   - Summary: ./data/processed/executive_summary.txt
```

**Runtime:** 3-5 minutes  
**Cost:** ~$0.30

---

### ☐ Step 7: Launch Dashboard

```bash
streamlit run src/app/dashboard.py
```

**Expected output:**
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.x:8501
```

**Browser will open automatically**

---

### ☐ Step 8: Explore Dashboard

**Check each tab:**

- [ ] **Overview** - See metrics and distributions
- [ ] **Theme Analysis** - Explore strategic themes
- [ ] **Quality Metrics** - Review quality scores
- [ ] **Alignment & Gaps** - Check team alignment
- [ ] **Search** - Try semantic search

**Try the filters:**
- [ ] Select different teams
- [ ] Filter by quarter
- [ ] Adjust visualizations

---

### ☐ Step 9: Export Results

```bash
python scripts/export_results.py
```

**Output:**
- `exports/okrs_[timestamp].csv`
- `exports/quality_scores_[timestamp].csv`
- `exports/themes_[timestamp].csv`
- `exports/alignment_matrix_[timestamp].csv`

**Also creates Excel (.xlsx) versions**

---

## Validation Checklist

### ☐ Verify Analysis Results

- [ ] Themes make sense for your organization
- [ ] Quality scores align with your assessment
- [ ] Alignment patterns match expectations
- [ ] Search returns relevant results

### ☐ Check Data Quality

- [ ] All 498 OKRs loaded correctly
- [ ] No missing teams or quarters
- [ ] Quality distribution looks reasonable
- [ ] No obvious errors in parsing

### ☐ Test Dashboard Features

- [ ] All tabs load without errors
- [ ] Charts display correctly
- [ ] Filters work as expected
- [ ] Search returns results
- [ ] Can export data

---

## Quick Reference

### Essential Commands

```bash
# Test without API key
python scripts/test_loader.py

# Run full analysis (requires API key)
python scripts/run_analysis.py

# Launch dashboard
streamlit run src/app/dashboard.py

# Export results
python scripts/export_results.py

# Clean and restart
python scripts/clean_data.py
```

### File Locations

```bash
# Configuration
.env                              # Your API key

# Input
data/okr_samples_500.txt          # OKR data

# Output
data/okr_results.db               # Database
data/processed/*.json             # Analysis results
data/chroma_db/                   # Vector index

# Exports
exports/*.csv                     # CSV exports
exports/*.xlsx                    # Excel exports
```

### Common Issues

| Symptom | Solution |
|---------|----------|
| "API key not found" | Add key to `.env` |
| "Module not found" | Run `pip install -r requirements.txt` |
| "No data found" | Run `python scripts/run_analysis.py` first |
| Dashboard empty | Check database exists |
| Slow performance | Reduce `MAX_WORKERS` in `.env` |

---

## Success Criteria

### ✅ You're successful when:

1. **Analysis completes** without errors
2. **Dashboard loads** and shows data
3. **Themes identified** (15-20 themes)
4. **Quality scores** calculated (50 samples)
5. **Alignment heatmap** displays
6. **Search works** and returns results
7. **Export creates** CSV/Excel files

### 📊 Expected Results:

- **Themes:** 15-20 strategic themes identified
- **Quality:** Average score 6-8 out of 10
- **Alignment:** Scores ranging 0.4-0.8
- **Runtime:** 3-5 minutes
- **Cost:** ~$0.30

---

## Next Steps After Setup

### Immediate (First Hour)

1. [ ] Review executive summary
2. [ ] Explore top themes
3. [ ] Check quality distribution
4. [ ] Identify improvement areas
5. [ ] Test semantic search

### Short-term (First Day)

1. [ ] Share dashboard with stakeholders
2. [ ] Export results to CSV/Excel
3. [ ] Validate insights with domain experts
4. [ ] Adjust prompts if needed
5. [ ] Document findings

### Medium-term (First Week)

1. [ ] Analyze all OKRs (not just samples)
2. [ ] Compare across quarters (if data available)
3. [ ] Deep dive into specific teams
4. [ ] Identify action items
5. [ ] Create improvement plan

### Long-term (First Month)

1. [ ] Integrate with existing tools
2. [ ] Automate regular analysis
3. [ ] Track improvements over time
4. [ ] Plan Azure migration
5. [ ] Scale to more OKRs

---

## Support Resources

### Documentation
- `README.md` - Overview and features
- `QUICKSTART.md` - 5-minute setup
- `USAGE_GUIDE.md` - Detailed usage
- `PROJECT_STRUCTURE.md` - Code organization

### Testing
- `scripts/test_loader.py` - Quick validation
- `tests/test_okr_loader.py` - Unit tests

### Configuration
- `.env.example` - Configuration template
- `src/utils/config.py` - Config management

---

## Final Checklist

Before considering setup complete:

- [ ] Python 3.10+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Gemini API key obtained
- [ ] `.env` file configured
- [ ] Test loader passes (`python scripts/test_loader.py`)
- [ ] Analysis runs successfully (`python scripts/run_analysis.py`)
- [ ] Dashboard loads (`streamlit run src/app/dashboard.py`)
- [ ] Can export results (`python scripts/export_results.py`)
- [ ] Results validated and make sense

---

## 🎉 You're Ready!

If all checkboxes are complete, your OKR Analysis System is fully operational.

**Start exploring your OKR insights!** 🎯

---

**Questions?** Review the documentation files or check the troubleshooting section.
