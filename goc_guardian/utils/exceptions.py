"""Custom exceptions for the CFP Reviewer Checker."""


class EvaluationError(Exception):
    """Base exception for evaluation-related errors."""

    pass


class APIUnavailableError(EvaluationError):
    """Raised when an external API is unavailable."""

    pass


class InvalidInputError(EvaluationError):
    """Raised when input validation fails."""

    pass

