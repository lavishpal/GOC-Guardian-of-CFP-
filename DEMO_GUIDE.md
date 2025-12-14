# CFP Guardian Demo Guide

## 🎯 Quick Summary

This project has **TWO similar implementations**:
1. **`goc_guardian/`** - Simplified, coordinator-based (RECOMMENDED for demo)
2. **`cfp_reviewer_checker/`** - More modular with corpus management

## 📦 Project Structure Explained

### ✅ Keep These:
- **`goc_guardian/`** - Main implementation with web UI and coordinator agents
- **`README.md`** - Project documentation
- **`requirements.txt`** - Python dependencies
- **`pyproject.toml`** - Package configuration
- **`example_usage.py`** - Usage examples

### ⚠️ Redundant (Consider Removing):
- **`cfp_reviewer_checker/`** - Alternative implementation with similar features
  - **Unique features**: CorpusManager (persistent storage), ParallelCrawler
  - **Decision**: Keep if you need persistent corpus storage, otherwise remove

### ❌ Should Remove:
- **`goc_guardian.egg-info/`** - Build artifacts (already in .gitignore)
  ```bash
  rm -rf goc_guardian.egg-info/
  ```

### 🔒 Already Properly Ignored:
- **`.venv/`** - Virtual environment (in .gitignore)
- **`.git/`** - Git repository (standard, keep)

---

## 🚀 Demo Preparation Steps

### Step 1: Environment Setup

```bash
# Navigate to project root
cd /Users/lavishpal/GOC-Guardian-of-CFP-

# Create/activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure API Keys

Create a `.env` file in the project root:

```bash
# Create .env file
cat > .env << 'EOF'
# Oumi API Configuration
OUMI_API_KEY=your_oumi_api_key_here
OUMI_BASE_URL=https://api.oumi.ai
OUMI_ENABLED=true

# Optional: Additional configurations
OUMI_TIMEOUT=30
OUMI_MAX_RETRIES=3
EOF
```

⚠️ **Important**: Get your Oumi API key from: https://oumi.ai (or your provider)

### Step 3: Choose Your Demo Approach

#### **Option A: Web UI Demo (RECOMMENDED)** 🌐

```bash
# Start the web server
python -m goc_guardian.web_app

# Open browser to: http://localhost:8000
```

**Demo Flow**:
1. Open browser to http://localhost:8000
2. Fill in the form:
   - **Title**: "Introduction to Microservices Architecture"
   - **Abstract**: Paste a sample CFP (see test scenarios below)
   - **Description**: (optional)
   - Check "Fetch Historical Talks"
3. Click "Analyze CFP"
4. Show the results:
   - Risk level
   - Similar talks found
   - Evaluation metrics
   - Recommendations

#### **Option B: Command Line Demo** 💻

```bash
# Run example
python example_usage.py

# Or analyze specific CFP
python -m goc_guardian.main "Your CFP text here..."
```

#### **Option C: Python API Demo** 🐍

```python
import asyncio
from goc_guardian.models import CFPSubmission
from goc_guardian.agents.enhanced_coordinator import EnhancedCoordinatorAgent

async def demo():
    coordinator = EnhancedCoordinatorAgent()
    
    cfp = CFPSubmission(
        title="Building Scalable Microservices with Python",
        abstract="This talk explores modern approaches to building microservices...",
        description="Attendees will learn practical patterns..."
    )
    
    report = await coordinator.analyze_cfp(cfp, fetch_historical=True)
    
    print(f"Risk Level: {report.overall_risk_level}")
    print(f"Similar Talks: {len(report.similar_talks)}")
    print(f"Originality: {report.evaluation_metrics.originality_score:.2f}")
    
    await coordinator.close()

asyncio.run(demo())
```

---

## 🧪 Test Scenarios for Demo

### Scenario 1: Generic CFP (Should flag as risky)

```text
Title: Introduction to Machine Learning

Abstract: This presentation will cover the fundamentals of machine learning, 
including supervised and unsupervised learning algorithms. We will explore 
various techniques and applications of ML in different domains. Attendees 
will gain insights into the latest trends and best practices in the field.
```

**Expected**: HIGH risk, low originality, generic content detected

### Scenario 2: Specific, Technical CFP (Should pass)

```text
Title: Optimizing PostgreSQL Query Performance in High-Throughput Systems

Abstract: Based on our experience scaling a fintech platform to 50M daily 
transactions, this talk presents specific techniques for PostgreSQL optimization. 
We'll cover: partition pruning strategies that reduced query time by 80%, 
effective use of materialized views with incremental refresh, and our custom 
connection pooling solution that eliminated timeout errors. Real production 
metrics and pgBadger analysis will be shared.
```

**Expected**: LOW risk, high originality, specific technical content

### Scenario 3: AI-Generated Sounding CFP (Should detect)

```text
Title: Leveraging Cutting-Edge Technologies for Digital Transformation

Abstract: In today's rapidly evolving landscape, it is imperative to harness 
innovative solutions that drive organizational excellence. This session will 
delve into transformative strategies, exploring how emerging technologies can 
revolutionize business processes. Furthermore, we will examine best practices 
and actionable insights to empower stakeholders in their journey towards 
digital maturity.
```

**Expected**: HIGH risk, AI-generated patterns detected, buzzword heavy

### Scenario 4: Duplicate/Similar Content (If historical data exists)

```text
Title: Getting Started with Docker Containers

Abstract: Docker has revolutionized application deployment. This talk covers 
Docker basics, containers vs VMs, creating Dockerfiles, and deploying 
containerized applications. Perfect for beginners wanting to learn Docker.
```

**Expected**: MEDIUM-HIGH risk, similar talks found (common topic)

---

## 🎬 Demo Presentation Flow

### 1. **Introduction** (2 min)
   - Problem: Conference reviewers need to detect copied/generic CFPs
   - Solution: AI-powered agent system using Oumi

### 2. **Architecture Overview** (3 min)
   - Show project structure
   - Explain agent-based design:
     - `AbstractAnalysisAgent`: Analyzes CFP content
     - `ContentEvaluationAgent`: Evaluates quality/originality
     - `EnhancedCoordinatorAgent`: Orchestrates the pipeline
   - Data sources: Sched.com, Sessionize.com
   - Evaluator: Oumi AI

### 3. **Live Demo** (10 min)
   - Start web UI
   - Run Scenario 1 (Generic CFP)
     - Show HIGH risk detection
     - Explain metrics
   - Run Scenario 2 (Technical CFP)
     - Show LOW risk
     - Highlight originality score
   - Run Scenario 3 (AI-generated)
     - Show detection of AI patterns

### 4. **Technical Deep Dive** (5 min)
   - Show code structure in `goc_guardian/agents/`
   - Demonstrate async processing
   - Explain Oumi integration in `evaluators/oumi_evaluator.py`

### 5. **Q&A** (5 min)

---

## 🔧 Troubleshooting

### Issue: Oumi API Not Available

```python
# The system handles this gracefully
# In oumi_client.py, it catches APIUnavailableError
```

**Workaround**: Set `OUMI_ENABLED=false` in `.env` to demo without Oumi

### Issue: No Historical Talks Found

- This is expected if Sched/Sessionize APIs are not configured
- The system will still analyze CFP content
- Focus on AI detection and content quality metrics

### Issue: Import Errors

```bash
# Ensure you're in the virtual environment
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

---

## 📊 What to Highlight in Demo

### ✅ Strengths:
1. **Agent-based architecture** - Modular, extensible
2. **Async processing** - Fast, efficient
3. **Graceful degradation** - Works even if APIs fail
4. **Real-world integration** - Sched.com, Sessionize.com
5. **AI-powered** - Oumi evaluation engine
6. **Reviewer-friendly UI** - Clear risk levels and recommendations

### 🎯 Use Cases:
1. Conference program committees
2. CFP screening automation
3. Plagiarism detection
4. Content quality assessment

---

## 🎨 Quick Cleanup Commands

```bash
# Remove build artifacts
rm -rf goc_guardian.egg-info/
rm -rf build/ dist/ *.egg-info/

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# (Optional) Remove redundant cfp_reviewer_checker
# ONLY if you decide you don't need corpus management
# rm -rf cfp_reviewer_checker/
```

---

## 📝 Post-Demo Next Steps

1. **Add Tests**:
   ```bash
   mkdir tests
   # Create test_agents.py, test_evaluators.py
   ```

2. **Add CI/CD**:
   - GitHub Actions for automated testing
   - Pre-commit hooks for code quality

3. **Enhance Features**:
   - Add more data sources
   - Implement caching
   - Add batch processing
   - Create dashboard for statistics

4. **Documentation**:
   - API documentation
   - Architecture diagrams
   - Contribution guidelines

---

## 🤝 Decision: Keep or Remove cfp_reviewer_checker?

### Keep if:
- You need **persistent corpus storage** (CorpusManager)
- You want **parallel crawling** infrastructure
- You plan to **merge** features into goc_guardian

### Remove if:
- You want a **single, clean** implementation
- You'll implement corpus management in goc_guardian later
- You prefer the coordinator-based architecture

**Recommendation**: Keep for now, cherry-pick unique features, then deprecate.

---

## 📞 Demo Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] `.env` file configured with API keys
- [ ] Web server tested (http://localhost:8000)
- [ ] Test scenarios prepared
- [ ] Build artifacts cleaned (`goc_guardian.egg-info/`)
- [ ] Backup slides/notes ready
- [ ] Network/internet connection verified
- [ ] Fallback plan if Oumi API fails

---

Good luck with your demo! 🚀
