# CFP Reviewer Checker

A production-quality, AI-powered, agent-based Python application that helps conference reviewers detect:
- Copied CFP abstracts/descriptions
- Near-duplicate or rewritten CFPs
- AI-generated or overly generic CFP content
- Semantically similar historical talks

## Features

- **Agent-Based Architecture**: Modular design with specialized agents for different analysis tasks
- **Oumi Integration**: Uses Oumi as the evaluation engine for semantic similarity, paraphrase detection, and AI content analysis
- **Historical Talk Fetching**: Automatically fetches historical accepted talks from Sched.com and Sessionize.com
- **Semantic Search**: Finds semantically similar talks using advanced similarity algorithms
- **Comprehensive Evaluation**: Evaluates semantic similarity, paraphrase likelihood, and AI-generated content patterns
- **Web UI**: Beautiful, modern web interface for easy use
- **Async Processing**: Efficient asynchronous processing for better performance
- **Reviewer-Friendly Output**: Explainable results designed for conference reviewers
- **Graceful Error Handling**: Fails gracefully when APIs are unavailable

## Requirements

- Python 3.10+
- See `requirements.txt` for dependencies

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Web UI (Recommended)

Start the web server:

```bash
python -m goc_guardian.web_app
```

Then open your browser to `http://localhost:8000` to access the web interface.

### Command Line

```bash
python -m goc_guardian.main <cfp_text>
```

Or analyze from a file:

```bash
python -m goc_guardian.main --file path/to/cfp.txt
```

### Python API

```python
import asyncio
from goc_guardian.models import CFPSubmission
from goc_guardian.agents.enhanced_coordinator import EnhancedCoordinatorAgent

async def analyze():
    coordinator = EnhancedCoordinatorAgent()
    
    cfp = CFPSubmission(
        title="Your CFP Title",
        abstract="Your CFP abstract here...",
        description="Optional description"
    )
    
    report = await coordinator.analyze_cfp(cfp, fetch_historical=True)
    
    print(f"Risk Level: {report.overall_risk_level}")
    print(f"Found {len(report.similar_talks)} similar talks")
    print(f"Originality: {report.evaluation_metrics.originality_score:.2f}")
    
    await coordinator.close()
    return report

# Run the analysis
report = asyncio.run(analyze())
```

## Project Structure

```
GOC-Guardian-of-CFP-/
├── goc_guardian/
│   ├── __init__.py
│   ├── main.py
│   ├── web_app.py
│   ├── models.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── abstract_analysis.py
│   │   ├── content_evaluation.py
│   │   ├── coordinator.py
│   │   └── enhanced_coordinator.py
│   ├── data_sources/
│   │   ├── __init__.py
│   │   ├── sched_client.py
│   │   ├── sessionize_client.py
│   │   └── semantic_search.py
│   ├── evaluators/
│   │   ├── __init__.py
│   │   └── oumi_evaluator.py
│   └── utils/
│       ├── __init__.py
│       └── exceptions.py
├── requirements.txt
├── pyproject.toml
├── README.md
└── .gitignore
```

## API Endpoints

When running the web app, the following endpoints are available:

- `GET /` - Web UI interface
- `POST /api/analyze` - Analyze a CFP submission (JSON)
- `GET /api/health` - Health check endpoint

## Configuration

You can configure API keys for Sched.com and Sessionize.com by setting environment variables:

```bash
export SCHED_API_KEY=your_sched_api_key
export SESSIONIZE_API_KEY=your_sessionize_api_key
```

Or pass them when initializing the coordinator:

```python
coordinator = EnhancedCoordinatorAgent(
    sched_api_key="your_key",
    sessionize_api_key="your_key"
)
```

## License

MIT

