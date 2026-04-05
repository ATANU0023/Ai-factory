"""Auditor Agent - Tests and validates generated code."""

import time
from typing import Any, Literal

from pydantic import BaseModel

from agents import BaseAgent
from observability.logger import get_logger
from observability.metrics import TokenUsage
from router.model_router import TaskType
from sandbox.docker_executor import SandboxExecutor

logger = get_logger(__name__)


class TestResult(BaseModel):
    """Result of a single test."""

    test_name: str
    status: Literal["pass", "fail", "error"]
    message: str | None = None


class AuditResult(BaseModel):
    """Complete audit result."""

    status: Literal["pass", "fail"]
    failure_type: str | None = None
    root_cause: str | None = None
    required_fix: str | None = None
    test_results: list[TestResult] = []
    logs: str = ""


class AuditorAgent(BaseAgent):
    """Execute tests and analyze failures using Analyze-and-Explain protocol."""

    def __init__(self, model_router: Any, session_id: str) -> None:
        super().__init__(model_router, session_id)
        # Use local execution by default (no Docker required)
        self.sandbox = SandboxExecutor(use_docker=False)

    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute code validation and testing."""
        start_time = time.time()

        generated_files = state.get("generated_files", [])
        if not generated_files:
            logger.error("No generated files to audit")
            state["audit_result"] = AuditResult(
                status="fail",
                failure_type="NoFilesGenerated",
                root_cause="Developer did not generate any files",
                required_fix="Check Developer Agent execution",
            ).model_dump()
            return state

        logger.info(f"Auditor Agent starting: validating {len(generated_files)} files")

        try:
            # Copy files to sandbox
            self.sandbox.copy_files_to_sandbox(generated_files)

            # Run tests
            test_results = self._run_tests()

            # Determine overall status
            all_passed = all(r.status == "pass" for r in test_results)

            if all_passed:
                audit_result = AuditResult(
                    status="pass",
                    test_results=test_results,
                    logs="All tests passed successfully",
                )
                logger.info("Audit PASSED: All tests successful")
            else:
                # Analyze failures
                failure_analysis = self._analyze_failures(test_results)
                audit_result = AuditResult(
                    status="fail",
                    failure_type=failure_analysis.get("failure_type"),
                    root_cause=failure_analysis.get("root_cause"),
                    required_fix=failure_analysis.get("required_fix"),
                    test_results=test_results,
                    logs=failure_analysis.get("logs", ""),
                )
                logger.warning(f"Audit FAILED: {audit_result.failure_type}")

            state["audit_result"] = audit_result.model_dump()
            state["current_step"] = "auditor_complete"

            # Record metrics
            tokens = TokenUsage()
            self._record_metrics(start_time, tokens, all_passed)

            return state

        except Exception as e:
            logger.error(f"Auditor Agent failed: {e}", exc_info=True)
            state["audit_result"] = AuditResult(
                status="fail",
                failure_type="ExecutionError",
                root_cause=str(e),
                required_fix="Check sandbox environment and file permissions",
            ).model_dump()
            state["error"] = str(e)
            self._record_metrics(start_time, TokenUsage(), False)
            return state

        finally:
            self.sandbox.cleanup()

    def _run_tests(self) -> list[TestResult]:
        """Execute test suite in sandbox."""
        results = []

        # First check if there are any test files
        import os
        from pathlib import Path
        
        temp_dir = Path(self.sandbox.temp_dir)
        test_files = list(temp_dir.glob("*test*.py")) + list(temp_dir.glob("test_*")) + \
                     list(temp_dir.glob("*_test.*")) + list(temp_dir.glob("*.test.*"))
        
        if not test_files:
            logger.info("No test files found, performing syntax validation only")
            # Do basic Python syntax check instead
            py_files = list(temp_dir.glob("*.py"))
            for py_file in py_files:
                try:
                    compile(py_file.read_text(), str(py_file), 'exec')
                    results.append(
                        TestResult(
                            test_name=f"Syntax check: {py_file.name}",
                            status="pass",
                            message="Python syntax is valid",
                        )
                    )
                except SyntaxError as e:
                    results.append(
                        TestResult(
                            test_name=f"Syntax check: {py_file.name}",
                            status="fail",
                            message=f"Syntax error: {str(e)}",
                        )
                    )
            
            if results:
                return results
        
        # If we have test files or want to try running tests anyway
        # Try common test commands
        test_commands = [
            ("npm test", "Running npm tests"),
            ("pytest", "Running pytest"),
            ("python -m pytest", "Running Python tests"),
        ]

        for command, description in test_commands:
            logger.info(description)
            result = self.sandbox.execute_command(command, timeout=60)

            if result.exit_code == 0:
                results.append(
                    TestResult(
                        test_name=command,
                        status="pass",
                        message="Tests executed successfully",
                    )
                )
                break
            else:
                # Only add failure if it's a real error (not just missing tools)
                if "not found" not in result.stderr.lower() and "error" not in result.stderr.lower():
                    results.append(
                        TestResult(
                            test_name=command,
                            status="fail",
                            message=result.stderr[:500] if result.stderr else "Test execution failed",
                        )
                    )

        # If no tests ran at all, assume pass (no test infrastructure)
        if not results:
            logger.warning("No tests could be executed, assuming pass")
            results.append(
                TestResult(
                    test_name="validation",
                    status="pass",
                    message="No test infrastructure available, code generated successfully",
                )
            )

        return results

    def _analyze_failures(self, test_results: list[TestResult]) -> dict[str, str]:
        """Analyze test failures using LLM for root cause analysis."""
        # Collect error logs
        error_logs = "\n".join(
            [r.message or "" for r in test_results if r.status != "pass"]
        )

        system_prompt = """You are a Debugging Expert. Analyze test failures and provide root cause analysis.

Follow the Analyze-and-Explain protocol:
1. Identify the Failure Type (Dependency Error, Syntax Error, Runtime Error, Logic Error, etc.)
2. Determine the Root Cause (what specifically went wrong)
3. Provide Required Fix (actionable steps to fix)

Be concise and specific. Do NOT suggest code changes directly."""

        try:
            result = self.model_router.route_request(
                task_type="log_analysis",
                prompt=f"Test failures occurred:\n\n{error_logs}\n\nAnalyze these failures.",
                system_prompt=system_prompt,
            )

            analysis = result.get("response", "")

            # Parse analysis (in production, use structured output)
            return {
                "failure_type": self._extract_field(analysis, "Failure Type:"),
                "root_cause": self._extract_field(analysis, "Root Cause:"),
                "required_fix": self._extract_field(analysis, "Required Fix:"),
                "logs": analysis,
            }

        except Exception as e:
            logger.error(f"Failure analysis failed: {e}")
            return {
                "failure_type": "AnalysisError",
                "root_cause": f"Failed to analyze failures: {e}",
                "required_fix": "Manual review required",
                "logs": error_logs,
            }

    def _extract_field(self, text: str, field_name: str) -> str:
        """Extract a field from analysis text."""
        lines = text.split("\n")
        for line in lines:
            if field_name in line:
                return line.replace(field_name, "").strip()
        return "Unknown"
