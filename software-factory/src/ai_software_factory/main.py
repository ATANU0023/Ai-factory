"""Main entry point for the Autonomous AI Software Factory."""

import argparse
import json
import sys
import uuid
from pathlib import Path

from ai_software_factory.config.settings import settings
from ai_software_factory.memory.vector_store import VectorStore
from ai_software_factory.observability.logger import get_logger
from ai_software_factory.observability.metrics import metrics_collector
from ai_software_factory.orchestrator.workflow_graph import WorkflowOrchestrator

logger = get_logger(__name__, interactive=False)


def run_factory(prompt: str, output_dir: str | None = None, clarifications: dict | None = None) -> dict:
    """Run the software factory with a given prompt."""
    # Generate session ID
    session_id = str(uuid.uuid4())
    logger.info(f"Starting new session: {session_id}")

    # Initialize metrics
    metrics_collector.create_session(session_id)

    try:
        # Execute workflow with clarifications
        orchestrator = WorkflowOrchestrator(session_id=session_id)
        
        # Prepare initial state with clarifications
        initial_state = {"user_input": prompt}
        if clarifications:
            initial_state["clarifications"] = clarifications
            logger.info(f"Using {len(clarifications)} clarification(s)")
        
        result = orchestrator.execute_from_state(initial_state)

        # Save results
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Save generated files info
            result_file = output_path / "result.json"
            result_file.write_text(json.dumps(result, indent=2), encoding="utf-8")

            logger.info(f"Results saved to: {result_file}")

        # Get metrics summary
        session_metrics = metrics_collector.get_session(session_id)
        if session_metrics:
            summary = session_metrics.get_summary()
            logger.info(f"Session metrics: {json.dumps(summary, indent=2)}")

        return result

    except Exception as e:
        logger.error(f"Factory execution failed: {e}", exc_info=True)
        return {
            "final_status": "failed",
            "error": str(e),
            "generated_files": [],
        }


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Autonomous AI Software Factory - Convert natural language to production code"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="Natural language description of the software to build",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=settings.project_output_dir,
        help="Directory to save generated project (default: ./output)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )

    args = parser.parse_args()

    if args.debug:
        settings.debug = True
        settings.log_level = "DEBUG"

    print("=" * 80)
    print("AUTONOMOUS AI SOFTWARE FACTORY")
    print("=" * 80)
    print(f"\nPrompt: {args.prompt}\n")
    print("Initializing agents...")

    # Run factory
    result = run_factory(args.prompt, args.output_dir)

    # Display results
    print("\n" + "=" * 80)
    print("EXECUTION COMPLETE")
    print("=" * 80)
    print(f"\nStatus: {result.get('final_status', 'unknown').upper()}")

    if result.get("error"):
        print(f"\nError: {result['error']}")

    generated_files = result.get("generated_files", [])
    if generated_files:
        print(f"\nGenerated {len(generated_files)} files:")
        for file_path in generated_files:
            print(f"  - {file_path}")

    if result.get("architect_plan"):
        plan = result["architect_plan"]
        print(f"\nProject: {plan.get('project_name', 'N/A')}")
        print(f"Architecture: {plan.get('architecture', 'N/A')}")
        print(f"Tech Stack: {', '.join(plan.get('tech_stack', []))}")

    print("\nCheck logs and metrics for detailed information.")
    print("=" * 80)

    # Exit with appropriate code
    if result.get("final_status") == "success":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
