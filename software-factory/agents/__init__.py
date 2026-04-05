"""Agent hierarchy for the Autonomous AI Software Factory."""

import time
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from observability.logger import get_logger
from observability.metrics import TokenUsage, metrics_collector
from router.model_router import ModelRouter, TaskType

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, model_router: ModelRouter, session_id: str) -> None:
        self.model_router = model_router
        self.session_id = session_id
        self.agent_name = self.__class__.__name__

    @abstractmethod
    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute agent logic and return updated state."""
        pass

    def _record_metrics(self, start_time: float, tokens: TokenUsage, success: bool) -> None:
        """Record execution metrics."""
        latency = time.time() - start_time
        metrics_collector.record_llm_call(
            session_id=self.session_id,
            agent_name=self.agent_name,
            prompt_tokens=tokens.prompt_tokens,
            completion_tokens=tokens.completion_tokens,
            cost_usd=tokens.cost_usd,
            latency_seconds=latency,
            success=success,
        )

    def _validate_output(self, output: BaseModel) -> bool:
        """Validate agent output using Pydantic validation."""
        try:
            output.model_validate(output)
            return True
        except Exception as e:
            logger.error(f"Output validation failed: {e}")
            return False


class TaskDefinition(BaseModel):
    """Definition of a development task."""

    task_id: str
    description: str
    files: list[str]
    dependencies: list[str]


class ArchitectPlan(BaseModel):
    """Structured output from Architect Agent."""

    project_name: str
    tech_stack: list[str]
    architecture: str
    services: list[dict[str, Any]]
    database_schema: list[dict[str, Any]]
    tasks: list[TaskDefinition]
