"""Supervisor Agent - Monitors workflow and handles failures."""

import time
from typing import Any

from ai_software_factory.agents import BaseAgent
from ai_software_factory.observability.logger import get_logger
from ai_software_factory.observability.metrics import TokenUsage, metrics_collector
from ai_software_factory.router.model_router import TaskType

logger = get_logger(__name__)


class SupervisorAgent(BaseAgent):
    """Monitor workflow, detect infinite loops, and intervene on failures."""

    MAX_DEBUG_CYCLES = 3

    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Monitor and intervene in workflow execution."""
        start_time = time.time()

        debug_cycles = state.get("debug_cycles", 0)
        audit_result = state.get("audit_result", {})

        logger.info(f"Supervisor Agent invoked: debug_cycles={debug_cycles}")

        # Check for excessive debug cycles (infinite loop detection)
        if debug_cycles >= self.MAX_DEBUG_CYCLES:
            logger.error(f"Maximum debug cycles ({self.MAX_DEBUG_CYCLES}) exceeded")
            return self._handle_max_retries_exceeded(state)

        # Analyze failure pattern
        if audit_result.get("status") == "fail":
            return self._handle_audit_failure(state, debug_cycles)

        # No issues detected
        state["supervisor_decision"] = "continue"
        state["current_step"] = "supervisor_complete"

        tokens = TokenUsage()
        self._record_metrics(start_time, tokens, True)
        return state

    def _handle_max_retries_exceeded(self, state: dict[str, Any]) -> dict[str, Any]:
        """Handle case where maximum retry attempts have been exhausted."""
        logger.error("Maximum retries exceeded - escalating to human review")

        session = metrics_collector.get_session(self.session_id)
        metrics_summary = session.get_summary() if session else {}

        state["final_status"] = "failed_max_retries"
        state["supervisor_decision"] = "escalate_to_human"
        state["escalation_reason"] = (
            f"Failed after {self.MAX_DEBUG_CYCLES} debug cycles. "
            f"Metrics: {metrics_summary}"
        )
        state["requires_human_review"] = True

        logger.warning(
            f"Escalating to human review. Session metrics: {metrics_summary}"
        )

        return state

    def _handle_audit_failure(self, state: dict[str, Any], debug_cycles: int) -> dict[str, Any]:
        """Handle audit failure with intervention strategy."""
        audit_result = state.get("audit_result", {})
        failure_type = audit_result.get("failure_type", "Unknown")
        root_cause = audit_result.get("root_cause", "Unknown")
        required_fix = audit_result.get("required_fix", "Unknown")

        logger.warning(
            f"Audit failure detected (cycle {debug_cycles + 1}): {failure_type}"
        )

        # Determine intervention strategy
        intervention = self._determine_intervention(failure_type, root_cause, debug_cycles)

        state["debug_cycles"] = debug_cycles + 1
        state["supervisor_decision"] = intervention["decision"]
        state["intervention_strategy"] = intervention

        # If revising plan, update architect instructions
        if intervention["decision"] == "revise_plan":
            state["architect_revision_needed"] = True
            state["revision_feedback"] = intervention.get("feedback", "")
            logger.info("Supervisor requesting architect plan revision")

        # If retrying developer, pass fix instructions
        elif intervention["decision"] == "retry_developer":
            state["developer_fix_instructions"] = required_fix
            logger.info(f"Supervisor instructing developer to fix: {required_fix[:100]}")

        tokens = TokenUsage()
        self._record_metrics(start_time, tokens, True)

        return state

    def _determine_intervention(
        self, failure_type: str, root_cause: str, debug_cycles: int
    ) -> dict[str, str]:
        """Determine appropriate intervention strategy based on failure analysis."""

        # Fundamental architecture issues - revise plan
        architecture_failures = [
            "ArchitectureError",
            "DesignFlaw",
            "IncompatibleStack",
        ]

        # Dependency or environment issues - can often be fixed by developer
        dependency_failures = [
            "DependencyError",
            "EnvironmentError",
            "ConfigurationError",
        ]

        # Code quality issues - developer should fix
        code_failures = [
            "SyntaxError",
            "RuntimeError",
            "LogicError",
            "TestFailure",
        ]

        if any(f in failure_type for f in architecture_failures):
            return {
                "decision": "revise_plan",
                "feedback": f"Fundamental issue detected: {root_cause}. Revise architecture.",
            }

        elif any(f in failure_type for f in dependency_failures):
            return {
                "decision": "retry_developer",
                "feedback": f"Dependency/environment issue: {root_cause}. Fix configuration.",
            }

        elif any(f in failure_type for f in code_failures):
            if debug_cycles < 2:
                return {
                    "decision": "retry_developer",
                    "feedback": f"Code issue: {root_cause}. Implement fix.",
                }
            else:
                # After multiple failed attempts, consider plan revision
                return {
                    "decision": "revise_plan",
                    "feedback": f"Repeated code failures: {root_cause}. Reconsider approach.",
                }

        else:
            # Unknown failure - conservative approach
            if debug_cycles < 1:
                return {
                    "decision": "retry_developer",
                    "feedback": f"Unknown failure: {root_cause}. Investigate and fix.",
                }
            else:
                return {
                    "decision": "escalate_to_human",
                    "feedback": f"Unresolvable failure after {debug_cycles} cycles: {root_cause}",
                }

    def check_cost_limits(self) -> dict[str, Any]:
        """Check if session is within cost governance limits."""
        session = metrics_collector.get_session(self.session_id)
        if not session:
            return {"within_limits": True}

        total_tokens = session.total_token_usage.total_tokens
        cost = session.total_token_usage.cost_usd

        token_limit = 500000  # From settings
        cost_limit = 10.0  # From settings

        warnings = []
        if total_tokens > token_limit * 0.8:
            warnings.append(f"Token usage at {total_tokens / token_limit * 100:.1f}% of limit")
        if cost > cost_limit * 0.8:
            warnings.append(f"Cost at ${cost:.2f}, {cost / cost_limit * 100:.1f}% of limit")

        return {
            "within_limits": total_tokens < token_limit and cost < cost_limit,
            "total_tokens": total_tokens,
            "current_cost": cost,
            "warnings": warnings,
        }
