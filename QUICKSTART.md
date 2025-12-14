# Quick Start Guide - CFP Guardian

## ⚡ 5-Minute Demo Setup

### 1. Install Dependencies (1 min)
```bash
# Activate virtual environment
source .venv/bin/activate

# Install packages
pip install -r requirements.txt

# Verify dynamic evaluation is working
python test_evaluator.py
```

You should see **different scores** for each test case. If you do, the fix is working! ✅

### 2. Configure Environment (1 min)
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OUMI_API_KEY
# (or set OUMI_ENABLED=false to test without Oumi)
```

### 3. Run Demo (3 min)

#### Option A: Web UI
```bash
python -m goc_guardian.web_app
# Open: http://localhost:8000
```

#### Option B: Test Scenarios
```bash
# Run all scenarios
python demo_test.py

# Run specific scenario
python demo_test.py generic
python demo_test.py specific
python demo_test.py ai_generated
```

#### Option C: Example Script
```bash
python example_usage.py
```

---

## 📋 Pre-Demo Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] `.env` file created with API key
- [ ] Ran cleanup: `./cleanup.sh`
- [ ] Web server works: `http://localhost:8000`
- [ ] Test scenarios work: `python demo_test.py`

---

## 🔧 Troubleshooting

### "No module named 'goc_guardian'"
```bash
# Install in development mode
pip install -e .
```

### "Oumi API unavailable"
```bash
# Set in .env:
OUMI_ENABLED=false
```

### "Permission denied: cleanup.sh"
```bash
chmod +x cleanup.sh
```

---

## 📚 More Information

- Full guide: `DEMO_GUIDE.md`
- Project README: `README.md`
- API usage: See `example_usage.py`

---

## 🎯 What This Project Does

**CFP Guardian** helps conference reviewers detect:
- ✅ Copied/plagiarized CFP content
- ✅ AI-generated submissions
- ✅ Generic/vague proposals
- ✅ Duplicate or near-duplicate talks

**How it works**:
1. Fetches historical accepted talks (Sched, Sessionize)
2. Compares CFP against historical data
3. Uses AI (Oumi) to evaluate semantic similarity
4. Provides risk assessment and recommendations

---

Good luck! 🚀
