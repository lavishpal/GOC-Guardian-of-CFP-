"""Main entry point for the CFP Reviewer Checker application."""

import asyncio
import sys
from typing import Optional
from goc_guardian.agents.coordinator import CoordinatorAgent
from goc_guardian.utils.exceptions import InvalidInputError, EvaluationError


async def analyze_cfp_text(cfp_text: str) -> None:
    """
    Analyze CFP text and print results.

    Args:
        cfp_text: The CFP text to analyze
    """
    coordinator = CoordinatorAgent()

    try:
        report = await coordinator.analyze_cfp(cfp_text)

        # Print results in a reviewer-friendly format
        print("\n" + "=" * 80)
        print("CFP REVIEWER CHECKER - ANALYSIS REPORT")
        print("=" * 80)
        print(f"\nOverall Risk Level: {report.overall_risk_level.upper()}")
        print("\n" + "-" * 80)
        print("SUMMARY")
        print("-" * 80)
        print(report.summary)
        print("\n" + "-" * 80)
        print("RECOMMENDATIONS")
        print("-" * 80)
        for i, rec in enumerate(report.recommendations, 1):
            print(f"{i}. {rec}")

        print("\n" + "-" * 80)
        print("DETAILED AGENT RESULTS")
        print("-" * 80)
        for result in report.agent_results:
            print(f"\n{result.agent_name}:")
            print(f"  Confidence: {result.confidence:.2f}")
            print(f"  Explanation: {result.explanation}")
            if "error" not in result.findings:
                print(f"  Findings: {result.findings}")

        print("\n" + "=" * 80 + "\n")

    except InvalidInputError as e:
        print(f"Error: Invalid input - {e}", file=sys.stderr)
        sys.exit(1)
    except EvaluationError as e:
        print(f"Error: Evaluation failed - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unexpected error - {e}", file=sys.stderr)
        sys.exit(1)


def read_cfp_from_file(file_path: str) -> str:
    """
    Read CFP text from a file.

    Args:
        file_path: Path to the file containing CFP text

    Returns:
        CFP text content

    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file cannot be read
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except IOError as e:
        raise IOError(f"Error reading file: {e}")


def main() -> None:
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m goc_guardian.main <cfp_text> | --file <file_path>", file=sys.stderr)
        print("\nOptions:", file=sys.stderr)
        print("  <cfp_text>        Direct CFP text to analyze", file=sys.stderr)
        print("  --file <file_path> Path to file containing CFP text", file=sys.stderr)
        sys.exit(1)

    cfp_text: Optional[str] = None

    if sys.argv[1] == "--file":
        if len(sys.argv) < 3:
            print("Error: --file requires a file path", file=sys.stderr)
            sys.exit(1)
        try:
            cfp_text = read_cfp_from_file(sys.argv[2])
        except (FileNotFoundError, IOError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Join all arguments as CFP text
        cfp_text = " ".join(sys.argv[1:])

    if not cfp_text:
        print("Error: No CFP text provided", file=sys.stderr)
        sys.exit(1)

    # Run async analysis
    asyncio.run(analyze_cfp_text(cfp_text))


if __name__ == "__main__":
    main()

