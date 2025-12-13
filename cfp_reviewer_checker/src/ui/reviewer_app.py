"""Reviewer web application using FastAPI."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn
from src.models.corpus_manager import CFPSubmission
from src.agents.conference_intelligence_agent import ConferenceIntelligenceAgent
from src.agents.similarity_detection_agent import SimilarityDetectionAgent
from src.agents.oumi_evaluation_agent import OumiEvaluationAgent
from src.agents.reviewer_decision_agent import ReviewerDecisionAgent
from src.ui.prompts import (
    generate_risk_explanation,
    generate_similarity_explanation,
    generate_ai_explanation,
    generate_originality_explanation,
)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(title="CFP Reviewer Checker", version="1.0.0")

    # Global agent instances
    conference_agent: Optional[ConferenceIntelligenceAgent] = None
    similarity_agent: Optional[SimilarityDetectionAgent] = None
    oumi_agent: Optional[OumiEvaluationAgent] = None
    decision_agent: Optional[ReviewerDecisionAgent] = None

    class CFPRequest(BaseModel):
        """Request model for CFP analysis."""

        title: str = Field(..., min_length=10, description="CFP title")
        abstract: str = Field(..., min_length=50, description="CFP abstract")
        description: Optional[str] = Field(None, description="CFP description (optional)")
        fetch_historical: bool = Field(True, description="Whether to fetch historical talks")

    @app.on_event("startup")
    async def startup():
        """Initialize agents on startup."""
        nonlocal conference_agent, similarity_agent, oumi_agent, decision_agent
        from src.models.corpus_manager import CorpusManager
        
        # Share corpus manager across agents
        corpus_manager = CorpusManager()
        conference_agent = ConferenceIntelligenceAgent(corpus_manager=corpus_manager)
        similarity_agent = SimilarityDetectionAgent(corpus_manager=corpus_manager)
        oumi_agent = OumiEvaluationAgent()
        decision_agent = ReviewerDecisionAgent()

    @app.on_event("shutdown")
    async def shutdown():
        """Clean up on shutdown."""
        nonlocal conference_agent
        if conference_agent:
            await conference_agent.close()

    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Serve the main web UI."""
        return get_ui_html()

    @app.post("/api/analyze")
    async def analyze_cfp(request: CFPRequest):
        """Analyze a CFP submission."""
        if not all([conference_agent, similarity_agent, oumi_agent, decision_agent]):
            raise HTTPException(status_code=503, detail="Service not initialized")

        try:
            cfp = CFPSubmission(
                title=request.title,
                abstract=request.abstract,
                description=request.description,
            )

            # Step 1: Conference intelligence - crawl and store talks
            if request.fetch_historical:
                # Optionally detect conferences from CFP, or crawl all
                await conference_agent.crawl_and_store(limit_per_platform=50)

            # Step 2: Similarity detection - retrieve from corpus (returns top 5)
            similar_talks = await similarity_agent.find_similar_talks(cfp)

            # Step 3: Oumi evaluation
            evaluation_metrics = await oumi_agent.evaluate(cfp, similar_talks)

            # Step 4: Generate final report
            report = decision_agent.generate_report(
                cfp, similar_talks, evaluation_metrics
            )

            # Return as dict for JSON serialization
            return report.model_dump()

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

    @app.get("/api/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "CFP Reviewer Checker"}

    return app


def get_ui_html() -> str:
    """Get HTML for the web UI."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CFP Reviewer Checker</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .content { padding: 40px; }
        .form-group { margin-bottom: 25px; }
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
        }
        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea { min-height: 120px; resize: vertical; }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 18px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4); }
        button:disabled { opacity: 0.6; cursor: not-allowed; }
        .loading { display: none; text-align: center; padding: 20px; color: #667eea; }
        .loading.active { display: block; }
        .results { display: none; margin-top: 40px; padding: 30px; background: #f8f9fa; border-radius: 8px; }
        .results.active { display: block; }
        .risk-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            margin-bottom: 20px;
        }
        .risk-high { background: #fee; color: #c33; }
        .risk-medium { background: #ffeaa7; color: #d63031; }
        .risk-low { background: #d5f4e6; color: #00b894; }
        .metric {
            background: white;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            display: none;
        }
        .error.active { display: block; }
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
                    <input type="text" id="title" name="title" required minlength="10">
                </div>
                <div class="form-group">
                    <label for="abstract">Abstract *</label>
                    <textarea id="abstract" name="abstract" required minlength="50"></textarea>
                </div>
                <div class="form-group">
                    <label for="description">Description (Optional)</label>
                    <textarea id="description" name="description"></textarea>
                </div>
                <button type="submit">Analyze CFP</button>
            </form>
            <div class="loading" id="loading">🔄 Analyzing CFP...</div>
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
            
            results.classList.remove('active');
            error.classList.remove('active');
            loading.classList.add('active');
            form.querySelector('button').disabled = true;
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        title: document.getElementById('title').value,
                        abstract: document.getElementById('abstract').value,
                        description: document.getElementById('description').value || null,
                        fetch_historical: true
                    })
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Analysis failed');
                }
                
                const data = await response.json();
                // Convert to ReviewerReport format if needed
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
            
            // Handle both old format and new ReviewerReport format
            const report = data.semantic_similarity !== undefined ? data : {
                semantic_similarity: data.evaluation_metrics?.semantic_similarity || 0,
                paraphrase_likelihood: data.evaluation_metrics?.paraphrase_likelihood || 0,
                ai_generation_confidence: data.evaluation_metrics?.ai_generation_probability || 0,
                originality_score: data.evaluation_metrics?.originality_score || 0,
                similar_talks: data.similar_talks || [],
                recommendation: data.recommendation || data.recommendations?.[0] || "No recommendation",
                explanation: data.explanation || data.summary || ""
            };
            
            const riskLevel = report.semantic_similarity > 0.8 || report.paraphrase_likelihood > 0.7 ? "high" :
                             report.semantic_similarity > 0.6 || report.paraphrase_likelihood > 0.5 ? "medium" : "low";
            const riskClass = `risk-${riskLevel}`;
            
            let html = `
                <div class="risk-badge ${riskClass}">
                    Recommendation: ${report.recommendation}
                </div>
                <div class="metric">
                    <strong>Semantic Similarity:</strong> ${(report.semantic_similarity * 100).toFixed(1)}%
                </div>
                <div class="metric">
                    <strong>Paraphrase Likelihood:</strong> ${(report.paraphrase_likelihood * 100).toFixed(1)}%
                </div>
                <div class="metric">
                    <strong>AI Generation Confidence:</strong> ${(report.ai_generation_confidence * 100).toFixed(1)}%
                </div>
                <div class="metric">
                    <strong>Originality Score:</strong> ${(report.originality_score * 100).toFixed(1)}%
                </div>
            `;
            
            if (report.similar_talks && report.similar_talks.length > 0) {
                html += '<h3>Similar Talks</h3>';
                report.similar_talks.slice(0, 5).forEach(talk => {
                    const title = talk.title || talk.talk?.title || "Unknown";
                    const similarity = talk.similarity_score || 0;
                    html += `<div class="metric">${title} (${(similarity * 100).toFixed(1)}% similar)</div>`;
                });
            }
            
            if (report.explanation) {
                html += '<h3>Explanation</h3>';
                html += `<div class="metric">${report.explanation.replace(/\n/g, '<br>')}</div>`;
            }
            
            results.innerHTML = html;
            results.classList.add('active');
        }
    </script>
</body>
</html>
    """


if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)

