"""Web application for CFP Reviewer Checker using FastAPI."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn
from goc_guardian.models import CFPSubmission
from goc_guardian.agents.enhanced_coordinator import EnhancedCoordinatorAgent
from goc_guardian.utils.exceptions import InvalidInputError, EvaluationError


app = FastAPI(title="CFP Reviewer Checker", version="1.0.0")

# Global coordinator instance
coordinator: Optional[EnhancedCoordinatorAgent] = None


class CFPRequest(BaseModel):
    """Request model for CFP analysis."""

    title: str = Field(..., min_length=10, description="CFP title")
    abstract: str = Field(..., min_length=50, description="CFP abstract")
    description: Optional[str] = Field(None, description="CFP description (optional)")
    fetch_historical: bool = Field(True, description="Whether to fetch historical talks")
    max_similar_talks: int = Field(10, ge=1, le=50, description="Maximum number of similar talks")


@app.on_event("startup")
async def startup():
    """Initialize coordinator on startup."""
    global coordinator
    coordinator = EnhancedCoordinatorAgent()


@app.on_event("shutdown")
async def shutdown():
    """Clean up on shutdown."""
    global coordinator
    if coordinator:
        await coordinator.close()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web UI."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CFP Reviewer Checker</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        .content {
            padding: 40px;
        }
        .form-group {
            margin-bottom: 25px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            font-family: inherit;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            min-height: 120px;
            resize: vertical;
        }
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        input[type="checkbox"] {
            width: 20px;
            height: 20px;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 18px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        button:active {
            transform: translateY(0);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #667eea;
        }
        .loading.active {
            display: block;
        }
        .results {
            display: none;
            margin-top: 40px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .results.active {
            display: block;
        }
        .risk-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            margin-bottom: 20px;
        }
        .risk-high {
            background: #fee;
            color: #c33;
        }
        .risk-medium {
            background: #ffeaa7;
            color: #d63031;
        }
        .risk-low {
            background: #d5f4e6;
            color: #00b894;
        }
        .metric {
            background: white;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .metric-label {
            font-weight: 600;
            color: #666;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 1.5em;
            color: #333;
        }
        .recommendations {
            margin-top: 20px;
        }
        .recommendation {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid #fdcb6e;
        }
        .similar-talks {
            margin-top: 20px;
        }
        .similar-talk {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid #74b9ff;
        }
        .similar-talk-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        .similar-talk-meta {
            font-size: 0.9em;
            color: #666;
        }
        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            display: none;
        }
        .error.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ CFP Reviewer Checker</h1>
            <p>AI-powered tool to detect copied, duplicate, and AI-generated CFP content</p>
        </div>
        <div class="content">
            <form id="cfpForm">
                <div class="form-group">
                    <label for="title">CFP Title *</label>
                    <input type="text" id="title" name="title" required minlength="10" 
                           placeholder="Enter the CFP title">
                </div>
                <div class="form-group">
                    <label for="abstract">Abstract *</label>
                    <textarea id="abstract" name="abstract" required minlength="50" 
                              placeholder="Enter the CFP abstract (minimum 50 characters)"></textarea>
                </div>
                <div class="form-group">
                    <label for="description">Description (Optional)</label>
                    <textarea id="description" name="description" 
                              placeholder="Enter additional CFP description"></textarea>
                </div>
                <div class="form-group">
                    <div class="checkbox-group">
                        <input type="checkbox" id="fetchHistorical" name="fetch_historical" checked>
                        <label for="fetchHistorical">Fetch historical talks from Sched.com and Sessionize.com</label>
                    </div>
                </div>
                <button type="submit">Analyze CFP</button>
            </form>
            <div class="loading" id="loading">
                <p>🔄 Analyzing CFP... This may take a moment.</p>
            </div>
            <div class="error" id="error"></div>
            <div class="results" id="results"></div>
        </div>
    </div>
    <script>
        document.getElementById('cfpForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const form = e.target;
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            const error = document.getElementById('error');
            
            // Hide previous results and errors
            results.classList.remove('active');
            error.classList.remove('active');
            loading.classList.add('active');
            form.querySelector('button').disabled = true;
            
            try {
                const formData = {
                    title: document.getElementById('title').value,
                    abstract: document.getElementById('abstract').value,
                    description: document.getElementById('description').value || null,
                    fetch_historical: document.getElementById('fetchHistorical').checked,
                    max_similar_talks: 10
                };
                
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Analysis failed');
                }
                
                const data = await response.json();
                displayResults(data);
                
            } catch (err) {
                error.textContent = 'Error: ' + err.message;
                error.classList.add('active');
            } finally {
                loading.classList.remove('active');
                form.querySelector('button').disabled = false;
            }
        });
        
        function displayResults(data) {
            const results = document.getElementById('results');
            const riskClass = `risk-${data.overall_risk_level}`;
            
            let html = `
                <div class="risk-badge ${riskClass}">
                    Risk Level: ${data.overall_risk_level.toUpperCase()}
                </div>
                <div class="metric">
                    <div class="metric-label">Originality Score</div>
                    <div class="metric-value">${(data.evaluation_metrics.originality_score * 100).toFixed(1)}%</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Paraphrase Likelihood</div>
                    <div class="metric-value">${(data.evaluation_metrics.paraphrase_likelihood * 100).toFixed(1)}%</div>
                </div>
                <div class="metric">
                    <div class="metric-label">AI Generation Probability</div>
                    <div class="metric-value">${(data.evaluation_metrics.ai_generation_probability * 100).toFixed(1)}%</div>
                </div>
            `;
            
            if (data.similar_talks && data.similar_talks.length > 0) {
                html += '<div class="similar-talks"><h3>Similar Historical Talks</h3>';
                data.similar_talks.slice(0, 5).forEach(talk => {
                    html += `
                        <div class="similar-talk">
                            <div class="similar-talk-title">${talk.talk.title}</div>
                            <div class="similar-talk-meta">
                                Similarity: ${(talk.similarity_score * 100).toFixed(1)}% | 
                                Paraphrase: ${(talk.paraphrase_likelihood * 100).toFixed(1)}%
                                ${talk.talk.conference ? ' | ' + talk.talk.conference : ''}
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
            }
            
            if (data.recommendations && data.recommendations.length > 0) {
                html += '<div class="recommendations"><h3>Recommendations</h3>';
                data.recommendations.forEach(rec => {
                    html += `<div class="recommendation">${rec}</div>`;
                });
                html += '</div>';
            }
            
            results.innerHTML = html;
            results.classList.add('active');
        }
    </script>
</body>
</html>
    """


@app.post("/api/analyze")
async def analyze_cfp(request: CFPRequest):
    """
    Analyze a CFP submission.

    Args:
        request: CFP submission data

    Returns:
        Analysis report
    """
    if not coordinator:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        cfp = CFPSubmission(
            title=request.title,
            abstract=request.abstract,
            description=request.description,
        )

        report = await coordinator.analyze_cfp(
            cfp,
            fetch_historical=request.fetch_historical,
            max_similar_talks=request.max_similar_talks,
        )

        # Convert to JSON-serializable format
        return {
            "cfp": {
                "title": report.cfp.title,
                "abstract": report.cfp.abstract,
                "description": report.cfp.description,
            },
            "similar_talks": [
                {
                    "talk": {
                        "title": st.talk.title,
                        "abstract": st.talk.abstract,
                        "description": st.talk.description,
                        "speaker": st.talk.speaker,
                        "conference": st.talk.conference,
                        "year": st.talk.year,
                        "source": st.talk.source,
                        "url": st.talk.url,
                    },
                    "similarity_score": st.similarity_score,
                    "paraphrase_likelihood": st.paraphrase_likelihood,
                }
                for st in report.similar_talks
            ],
            "evaluation_metrics": {
                "semantic_similarity": report.evaluation_metrics.semantic_similarity,
                "paraphrase_likelihood": report.evaluation_metrics.paraphrase_likelihood,
                "ai_generation_probability": report.evaluation_metrics.ai_generation_probability,
                "originality_score": report.evaluation_metrics.originality_score,
            },
            "overall_risk_level": report.overall_risk_level,
            "summary": report.summary,
            "recommendations": report.recommendations,
        }

    except InvalidInputError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EvaluationError as e:
        raise HTTPException(status_code=500, detail=f"Evaluation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "CFP Reviewer Checker"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

