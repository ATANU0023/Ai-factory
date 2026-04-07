"""LangGraph-based workflow orchestration for multi-agent system."""

from typing import Any, Literal

from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from ai_software_factory.agents.architect_agent import ArchitectAgent
from ai_software_factory.agents.auditor_agent import AuditorAgent
from ai_software_factory.agents.developer_agent import DeveloperAgent
from ai_software_factory.agents.supervisor_agent import SupervisorAgent
from ai_software_factory.memory.semantic_cache import SemanticCache
from ai_software_factory.observability.logger import get_logger
from ai_software_factory.router.model_router import ModelRouter

logger = get_logger(__name__)


class WorkflowState(TypedDict):
    """State schema for the workflow graph."""

    user_input: str
    architect_plan: dict[str, Any] | None
    generated_files: list[str]
    audit_result: dict[str, Any] | None
    debug_cycles: int
    current_step: str
    supervisor_decision: str | None
    final_status: str | None
    error: str | None
    developer_fix_instructions: str | None
    architect_revision_needed: bool
    revision_feedback: str | None


class WorkflowOrchestrator:
    """Orchestrate multi-agent workflow using LangGraph."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self.model_router = ModelRouter(session_id=session_id)
        self.semantic_cache = SemanticCache()

        # Initialize agents
        self.architect = ArchitectAgent(
            model_router=self.model_router,
            session_id=session_id,
        )
        self.developer = DeveloperAgent(
            model_router=self.model_router,
            session_id=session_id,
        )
        self.auditor = AuditorAgent(
            model_router=self.model_router,
            session_id=session_id,
        )
        self.supervisor = SupervisorAgent(
            model_router=self.model_router,
            session_id=session_id,
        )

        # Build workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("architect", self.architect.execute)
        workflow.add_node("developer", self.developer.execute)
        workflow.add_node("auditor", self.auditor.execute)
        workflow.add_node("supervisor", self.supervisor.execute)

        # Define edges
        workflow.add_edge(START, "architect")
        workflow.add_edge("architect", "developer")
        workflow.add_edge("developer", "auditor")

        # Conditional routing after auditor
        workflow.add_conditional_edges(
            "auditor",
            self._route_after_audit,
            {
                "pass": END,
                "retry_developer": "developer",
                "revise_plan": "architect",
                "supervisor": "supervisor",
            },
        )

        return workflow.compile()

    def _route_after_audit(self, state: WorkflowState) -> str:
        """Determine next step after audit."""
        audit_result = state.get("audit_result")

        if not audit_result:
            logger.warning("No audit result found, defaulting to supervisor")
            return "supervisor"

        status = audit_result.get("status")

        if status == "pass":
            logger.info("Audit passed - workflow complete")
            return "pass"

        # Audit failed - check debug cycles
        debug_cycles = state.get("debug_cycles", 0)

        if debug_cycles >= 3:
            logger.warning("Max debug cycles reached - escalating to supervisor")
            return "supervisor"

        # Determine retry strategy based on failure type
        failure_type = audit_result.get("failure_type", "")

        if "Architecture" in failure_type or "Design" in failure_type:
            return "revise_plan"
        else:
            return "retry_developer"

    def _route_after_supervisor(self, state: WorkflowState) -> str:
        """Determine next step after supervisor intervention."""
        decision = state.get("supervisor_decision", "continue")
        logger.info(f"Supervisor decision: {decision}")
        return decision

    def execute(self, user_input: str) -> dict[str, Any]:
        """Execute the full workflow."""
        initial_state = {"user_input": user_input}
        return self.execute_from_state(initial_state)

    def execute_from_state(self, initial_state: dict[str, Any]) -> dict[str, Any]:
        """Execute workflow from a custom initial state (supports clarifications)."""
        user_input = initial_state.get("user_input", "")
        logger.info(f"Starting workflow for: {user_input[:100]}...")

        # Merge with default state
        default_state: WorkflowState = {
            "user_input": user_input,
            "architect_plan": None,
            "generated_files": [],
            "audit_result": None,
            "debug_cycles": 0,
            "current_step": "start",
            "supervisor_decision": None,
            "final_status": None,
            "error": None,
            "developer_fix_instructions": None,
            "architect_revision_needed": False,
            "revision_feedback": None,
        }
        
        # Update with provided state (e.g., clarifications)
        default_state.update(initial_state)

        try:
            # Execute workflow with recursion limit to prevent infinite loops
            config = {"recursion_limit": 50}  # Limit to 50 steps max
            final_state = self.workflow.invoke(default_state, config=config)

            # Determine final status
            if final_state.get("error"):
                final_state["final_status"] = "failed"
                logger.error(f"Workflow failed: {final_state['error']}")
            elif final_state.get("requires_human_review"):
                final_state["final_status"] = "requires_human_review"
                logger.warning("Workflow requires human review")
            else:
                final_state["final_status"] = "success"
                logger.info("Workflow completed successfully")

            return final_state

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}", exc_info=True)
            return {
                "user_input": user_input,
                "final_status": "failed",
                "error": str(e),
                "generated_files": [],
            }
