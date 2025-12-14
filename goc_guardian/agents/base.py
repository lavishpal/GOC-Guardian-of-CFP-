"""Base agent class for the GOC: Guardians of CFP."""

from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel


class AgentResult(BaseModel):
    """Base model for agent analysis results."""

    agent_name: str
    confidence: float  # 0.0 to 1.0
    findings: Dict[str, Any]
    explanation: str


class BaseAgent(ABC):
    """Base class for all agents in the GOC: Guardians of CFP."""

    def __init__(self, name: str):
        """
        Initialize the base agent.

        Args:
            name: Name of the agent
        """
        self.name = name

    @abstractmethod
    async def analyze(self, cfp_text: str) -> AgentResult:
        """
        Analyze CFP text and return results.

        Args:
            cfp_text: The CFP text to analyze

        Returns:
            AgentResult containing analysis findings

        Raises:
            EvaluationError: If analysis fails
        """
        pass

    def _validate_input(self, cfp_text: str) -> None:
        """
        Validate input CFP text.

        Args:
            cfp_text: The CFP text to validate

        Raises:
            InvalidInputError: If input is invalid
        """
        if not cfp_text or not isinstance(cfp_text, str):
            raise InvalidInputError("CFP text must be a non-empty string")
        if len(cfp_text.strip()) < 50:
            raise InvalidInputError("CFP text must be at least 50 characters long")

