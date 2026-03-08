# 🎯 START HERE - OKR Analysis System

## 👋 Welcome!

Your OKR Analysis System is **ready to use**. This guide will get you started in **5 minutes**.

---

## ⚡ Quick Start (3 Steps)

### Step 1: Install Dependencies (2 minutes)

```bash
pip install -r requirements.txt
```

Wait for installation to complete...

---

### Step 2: Add Your API Key (1 minute)

```bash
# Copy the template
cp .env.example .env

# Edit the file
nano .env  # or use any text editor
```

**Change this line:**
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

**To your actual key:**
```bash
GEMINI_API_KEY=AIzaSy...your_key
```

**Don't have a key?** Get one here: https://makersuite.google.com/app/apikey (free)

---

### Step 3: Run Analysis (3-5 minutes)

```bash
python scripts/run_analysis.py
```

**This will:**
- ✓ Load 498 OKRs
- ✓ Split into 4 chunks
- ✓ Extract themes (parallel)
- ✓ Assess quality (50 samples)
- ✓ Compute alignment
- ✓ Generate summary

**Cost:** ~$0.30

---

## 🎨 View Results

```bash
streamlit run src/app/dashboard.py
```

**Opens at:** http://localhost:8501

**Explore:**
- 📈 Overview - Key metrics
- 🎨 Themes - Strategic themes
- ⭐ Quality - Quality scores
- 🔗 Alignment - Team alignment
- 🔍 Search - Semantic search

---

## 📊 What You'll Get

### Themes (Example)
```
1. Customer Experience (45 OKRs)
2. Operational Efficiency (38 OKRs)
3. Digital Transformation (32 OKRs)
4. Revenue Growth (28 OKRs)
5. Employee Development (25 OKRs)
...
```

### Quality Scores (Example)
```
Average: 7.2/10
High Quality (8+): 18 OKRs
Good (6-8): 24 OKRs
Needs Improvement (<6): 8 OKRs
```

### Alignment Matrix (Example)
```
Engineering ↔ IT: 0.82 (Strong)
Sales ↔ Marketing: 0.71 (Good)
HR ↔ Finance: 0.58 (Moderate)
Sales ↔ HR: 0.45 (Weak)
```

---

## 🆘 Troubleshooting

### "API key not found"
→ Check `.env` file exists and has your key

### "Module not found"
→ Run: `pip install -r requirements.txt`

### "No data found"
→ Run analysis first: `python scripts/run_analysis.py`

### Dashboard is empty
→ Check `data/okr_results.db` exists

---

## 📚 Need More Help?

| Question | Read This |
|----------|-----------|
| How do I set up? | `QUICKSTART.md` |
| How do I use it? | `USAGE_GUIDE.md` |
| Step-by-step guide? | `GETTING_STARTED.md` |
| What was built? | `IMPLEMENTATION_SUMMARY.md` |
| Code structure? | `PROJECT_STRUCTURE.md` |
| Features overview? | `README.md` |

---

## ✅ Verification

After running analysis, you should have:

- [x] **Console output** showing progress
- [x] **Executive summary** printed at end
- [x] **Files created:**
  - `data/okr_results.db` (SQLite)
  - `data/chroma_db/` (vectors)
  - `data/processed/themes.json`
  - `data/processed/quality_scores.json`
  - `data/processed/alignment.json`
  - `data/processed/executive_summary.txt`

---

## 🎯 Your Data

**Input File:** `data/okr_samples_500.txt`

**Statistics:**
- Total OKRs: 498
- Teams: 4 (Engineering, Sales, HR, IT)
- Quarter: Q1 2024
- Quality Levels: High (137), Medium (232), Low (129)

**Processing:**
- Split into 4 chunks: [125, 125, 125, 123]
- Processed in parallel
- All OKRs indexed for search

---

## 🚀 Ready to Go!

### Your command sequence:

```bash
# 1. Install (one-time)
pip install -r requirements.txt

# 2. Configure (one-time)
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 3. Analyze (3-5 minutes)
python scripts/run_analysis.py

# 4. View (instant)
streamlit run src/app/dashboard.py
```

---

## 💡 Pro Tips

1. **Test first:** Run `python scripts/test_loader.py` to verify setup
2. **Start small:** Default settings are optimized for quick results
3. **Review prompts:** Check `src/utils/llm_client.py` for customization
4. **Export results:** Use `python scripts/export_results.py` for CSV/Excel
5. **Clean slate:** Run `python scripts/clean_data.py` to reset

---

## 🎉 That's It!

You're ready to analyze your OKRs.

**Start now:**
```bash
python scripts/run_analysis.py
```

**Questions?** Check the documentation files listed above.

---

**Built with:** Python • Gemini Flash 2.0 • ChromaDB • Streamlit  
**Ready for:** Azure Migration • Production Deployment • Scale-up
