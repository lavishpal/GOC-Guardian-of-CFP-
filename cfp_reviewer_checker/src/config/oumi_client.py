"""Oumi client configuration and client setup."""

import os
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from src.utils.exceptions import APIUnavailableError, EvaluationError


class OumiConfig(BaseModel):
    """Configuration for Oumi client."""

    api_key: Optional[str] = Field(None, description="Oumi API key")
    base_url: str = Field("https://api.oumi.ai", description="Oumi API base URL")
    timeout: int = Field(30, description="Request timeout in seconds")
    max_retries: int = Field(3, description="Maximum number of retries")
    enabled: bool = Field(True, description="Whether Oumi evaluation is enabled")

    @classmethod
    def from_env(cls) -> "OumiConfig":
        """
        Create configuration from environment variables.

        Returns:
            OumiConfig instance
        """
        return cls(
            api_key=os.getenv("OUMI_API_KEY"),
            base_url=os.getenv("OUMI_BASE_URL", "https://api.oumi.ai"),
            timeout=int(os.getenv("OUMI_TIMEOUT", "30")),
            max_retries=int(os.getenv("OUMI_MAX_RETRIES", "3")),
            enabled=os.getenv("OUMI_ENABLED", "true").lower() == "true",
        )


class OumiClient:
    """Client for interacting with Oumi API."""

    def __init__(self, config: Optional[OumiConfig] = None):
        """
        Initialize Oumi client.

        Args:
            config: Oumi configuration, or None to load from environment
        """
        self.config = config or OumiConfig.from_env()
        self._available = self.config.enabled
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _call_oumi_api(
        self, endpoint: str, payload: Dict[str, Any], retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Call Oumi API with retry logic.

        Args:
            endpoint: API endpoint
            payload: Request payload
            retry_count: Current retry count

        Returns:
            API response as dictionary

        Raises:
            APIUnavailableError: If API is unavailable
            EvaluationError: If evaluation fails
        """
        if not self._available:
            raise APIUnavailableError("Oumi client is not available")

        if not self.config.api_key:
            raise APIUnavailableError("Oumi API key not configured")

        try:
            session = await self._get_session()
            url = f"{self.config.base_url}/{endpoint}"

            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            }

            async with session.post(
                url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    raise APIUnavailableError("Invalid Oumi API key")
                elif response.status >= 500 and retry_count < self.config.max_retries:
                    # Retry on server errors
                    await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                    return await self._call_oumi_api(endpoint, payload, retry_count + 1)
                else:
                    error_text = await response.text()
                    raise EvaluationError(
                        f"Oumi API error (status {response.status}): {error_text}"
                    )

        except aiohttp.ClientError as e:
            if retry_count < self.config.max_retries:
                await asyncio.sleep(2 ** retry_count)
                return await self._call_oumi_api(endpoint, payload, retry_count + 1)
            raise APIUnavailableError(f"Oumi API connection error: {str(e)}")

    async def evaluate_semantic_similarity(
        self, text1: str, text2: str
    ) -> Dict[str, Any]:
        """
        Evaluate semantic similarity between two texts using Oumi.

        Args:
            text1: First text (CFP submission)
            text2: Second text (historical talk)

        Returns:
            Dictionary with similarity score and explanation:
            {
                "score": float (0.0 to 1.0),
                "explanation": str
            }
        """
        try:
            response = await self._call_oumi_api(
                "evaluate/similarity",
                {
                    "text1": text1,
                    "text2": text2,
                    "metric": "semantic_similarity",
                },
            )

            # Extract numeric score and explanation from Oumi response
            return {
                "score": float(response.get("score", 0.0)),
                "explanation": response.get("explanation", "Semantic similarity evaluated by Oumi"),
            }
        except (APIUnavailableError, EvaluationError):
            raise
        except Exception as e:
            raise EvaluationError(f"Semantic similarity evaluation failed: {str(e)}")

    async def evaluate_paraphrase(self, text1: str, text2: str) -> Dict[str, Any]:
        """
        Evaluate paraphrase likelihood between two texts using Oumi.

        Args:
            text1: First text (CFP submission)
            text2: Second text (historical talk)

        Returns:
            Dictionary with paraphrase score and explanation:
            {
                "score": float (0.0 to 1.0),
                "explanation": str
            }
        """
        try:
            response = await self._call_oumi_api(
                "evaluate/paraphrase",
                {
                    "text1": text1,
                    "text2": text2,
                    "metric": "paraphrase_detection",
                },
            )

            return {
                "score": float(response.get("score", 0.0)),
                "explanation": response.get("explanation", "Paraphrase likelihood evaluated by Oumi"),
            }
        except (APIUnavailableError, EvaluationError):
            raise
        except Exception as e:
            raise EvaluationError(f"Paraphrase evaluation failed: {str(e)}")

    async def evaluate_ai_generation(self, text: str) -> Dict[str, Any]:
        """
        Evaluate AI generation probability using Oumi.

        Args:
            text: Text to evaluate

        Returns:
            Dictionary with AI generation score and explanation:
            {
                "score": float (0.0 to 1.0),
                "explanation": str
            }
        """
        try:
            response = await self._call_oumi_api(
                "evaluate/ai-detection",
                {
                    "text": text,
                    "metric": "ai_generation",
                },
            )

            return {
                "score": float(response.get("score", 0.0)),
                "explanation": response.get("explanation", "AI generation patterns evaluated by Oumi"),
            }
        except (APIUnavailableError, EvaluationError):
            raise
        except Exception as e:
            raise EvaluationError(f"AI generation evaluation failed: {str(e)}")

    async def evaluate_originality(
        self, text: str, reference_texts: list[str]
    ) -> Dict[str, Any]:
        """
        Evaluate originality score using Oumi.

        Args:
            text: Text to evaluate
            reference_texts: List of reference texts for comparison

        Returns:
            Dictionary with originality score and explanation:
            {
                "score": float (0.0 to 1.0),
                "explanation": str
            }
        """
        try:
            response = await self._call_oumi_api(
                "evaluate/originality",
                {
                    "text": text,
                    "reference_texts": reference_texts,
                    "metric": "originality",
                },
            )

            return {
                "score": float(response.get("score", 0.5)),
                "explanation": response.get("explanation", "Originality evaluated by Oumi"),
            }
        except (APIUnavailableError, EvaluationError):
            raise
        except Exception as e:
            raise EvaluationError(f"Originality evaluation failed: {str(e)}")

    def set_available(self, available: bool) -> None:
        """
        Set availability status.

        Args:
            available: Whether the client is available
        """
        self._available = available and self.config.enabled

