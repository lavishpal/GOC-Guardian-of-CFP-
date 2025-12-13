# CFP Reviewer Checker

A production-quality, AI-powered, agent-based Python application that helps conference reviewers detect:
- Copied CFP abstracts/descriptions
- Near-duplicate or rewritten CFPs
- AI-generated or overly generic CFP content
- Semantically similar historical talks

## Features

- **Agent-Based Architecture**: Specialized agents for conference intelligence, similarity detection, Oumi evaluation, and reviewer decisions
- **Historical Talk Fetching**: Automatically fetches historical accepted talks from Sched.com and Sessionize.com
- **Semantic Search**: Finds semantically similar talks using advanced similarity algorithms
- **Oumi Integration**: Uses Oumi for semantic similarity, paraphrase detection, and AI content analysis
- **Web UI**: Beautiful, modern web interface for easy use
- **Corpus Management**: Persistent storage and management of historical talks
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

Copy `.env.example` to `.env` and configure your API keys:

```bash
cp .env.example .env
# Edit .env with your API keys
```

## Usage

### Web UI (Recommended)

Start the web server:

```bash
python -m src.ui.reviewer_app
```

Or:

```bash
python main.py --web
```

Then open your browser to `http://localhost:8000` to access the web interface.

### Command Line

```bash
python main.py "CFP Title" "CFP abstract text here..." "Optional description"
```

### Python API

```python
import asyncio
from src.models.corpus_manager import CFPSubmission
from src.agents.conference_intelligence_agent import ConferenceIntelligenceAgent
from src.agents.similarity_detection_agent import SimilarityDetectionAgent
from src.agents.oumi_evaluation_agent import OumiEvaluationAgent
from src.agents.reviewer_decision_agent import ReviewerDecisionAgent

async def analyze():
    # Initialize agents
    conference_agent = ConferenceIntelligenceAgent()
    similarity_agent = SimilarityDetectionAgent()
    oumi_agent = OumiEvaluationAgent()
    decision_agent = ReviewerDecisionAgent()
    
    # Create CFP submission
    cfp = CFPSubmission(
        title="Your CFP Title",
        abstract="Your CFP abstract here...",
        description="Optional description"
    )
    
    # Run analysis pipeline
    conference_result = await conference_agent.analyze(cfp)
    historical_talks = conference_result.get("historical_talks", [])
    
    similar_talks = await similarity_agent.find_similar_talks(cfp, historical_talks)
    evaluation_metrics = await oumi_agent.evaluate(cfp, similar_talks)
    report = decision_agent.generate_report(cfp, similar_talks, evaluation_metrics)
    
    await conference_agent.close()
    return report

# Run the analysis
report = asyncio.run(analyze())
```

## Project Structure

```
cfp_reviewer_checker/
├── main.py                          # CLI entry point
├── src/
│   ├── agents/
│   │   ├── conference_intelligence_agent.py
│   │   ├── similarity_detection_agent.py
│   │   ├── oumi_evaluation_agent.py
│   │   └── reviewer_decision_agent.py
│   ├── scrapers/
│   │   ├── conference_detector.py
│   │   ├── parallel_crawler.py
│   │   └── platform_adapters.py
│   ├── models/
│   │   └── corpus_manager.py
│   ├── evaluation/
│   │   └── oumi_pipeline.py
│   ├── config/
│   │   └── oumi_client.py
│   └── ui/
│       ├── reviewer_app.py
│       └── prompts.py
├── README.md
├── requirements.txt
└── .env.example
```

## Configuration

Configure the application via environment variables (see `.env.example`):

- `OUMI_API_KEY`: Oumi API key for evaluation
- `SCHED_API_KEY`: Sched.com API key (optional)
- `SESSIONIZE_API_KEY`: Sessionize.com API key (optional)
- `CORPUS_STORAGE_PATH`: Path to corpus storage file (default: `./corpus.json`)

## API Endpoints

When running the web app:

- `GET /` - Web UI interface
- `POST /api/analyze` - Analyze a CFP submission (JSON)
- `GET /api/health` - Health check endpoint

## License

MIT

