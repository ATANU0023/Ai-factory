"""Metrics collection for token usage, cost, latency, and agent actions."""

import time
from dataclasses import dataclass, field
from typing import Any

from ai_software_factory.observability.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TokenUsage:
    """Track token usage metrics."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0

    def add_usage(self, prompt: int, completion: int, cost: float) -> None:
        """Add token usage from an LLM call."""
        self.prompt_tokens += prompt
        self.completion_tokens += completion
        self.total_tokens += prompt + completion
        self.cost_usd += cost


@dataclass
class AgentMetrics:
    """Track metrics for a specific agent."""

    agent_name: str
    execution_count: int = 0
    total_latency_seconds: float = 0.0
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    error_count: int = 0
    success_count: int = 0

    def record_execution(self, latency: float, tokens: TokenUsage, success: bool) -> None:
        """Record a single agent execution."""
        self.execution_count += 1
        self.total_latency_seconds += latency
        self.token_usage.add_usage(tokens.prompt_tokens, tokens.completion_tokens, tokens.cost_usd)
        if success:
            self.success_count += 1
        else:
            self.error_count += 1

    @property
    def avg_latency(self) -> float:
        """Calculate average latency per execution."""
        if self.execution_count == 0:
            return 0.0
        return self.total_latency_seconds / self.execution_count


@dataclass
class SessionMetrics:
    """Track metrics for an entire session."""

    session_id: str
    start_time: float = field(default_factory=time.time)
    agent_metrics: dict[str, AgentMetrics] = field(default_factory=dict)
    total_token_usage: TokenUsage = field(default_factory=TokenUsage)
    tasks_completed: int = 0
    tasks_failed: int = 0

    def get_or_create_agent_metrics(self, agent_name: str) -> AgentMetrics:
        """Get or create agent metrics."""
        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = AgentMetrics(agent_name=agent_name)
        return self.agent_metrics[agent_name]

    def record_task_completion(self, success: bool) -> None:
        """Record task completion."""
        if success:
            self.tasks_completed += 1
        else:
            self.tasks_failed += 1

    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        return time.time() - self.start_time

    def get_summary(self) -> dict[str, Any]:
        """Get metrics summary."""
        return {
            "session_id": self.session_id,
            "elapsed_time_seconds": round(self.elapsed_time, 2),
            "total_tokens": self.total_token_usage.total_tokens,
            "total_cost_usd": round(self.total_token_usage.cost_usd, 4),
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "agent_metrics": {
                name: {
                    "executions": metrics.execution_count,
                    "avg_latency": round(metrics.avg_latency, 2),
                    "tokens": metrics.token_usage.total_tokens,
                    "errors": metrics.error_count,
                }
                for name, metrics in self.agent_metrics.items()
            },
        }


class MetricsCollector:
    """Centralized metrics collection."""

    def __init__(self) -> None:
        self.active_sessions: dict[str, SessionMetrics] = {}

    def create_session(self, session_id: str) -> SessionMetrics:
        """Create a new session."""
        session = SessionMetrics(session_id=session_id)
        self.active_sessions[session_id] = session
        logger.info(f"Created metrics session: {session_id}")
        return session

    def get_session(self, session_id: str) -> SessionMetrics | None:
        """Get existing session."""
        return self.active_sessions.get(session_id)

    def record_llm_call(
        self,
        session_id: str,
        agent_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
        latency_seconds: float,
        success: bool,
    ) -> None:
        """Record an LLM call."""
        session = self.get_session(session_id)
        if not session:
            # Auto-create session for transient queries (like CLI conversation)
            session = self.create_session(session_id)
            logger.debug(f"Auto-created metrics session: {session_id}")
        
        tokens = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            cost_usd=cost_usd,
        )

        agent_metrics = session.get_or_create_agent_metrics(agent_name)
        agent_metrics.record_execution(latency_seconds, tokens, success)
        session.total_token_usage.add_usage(prompt_tokens, completion_tokens, cost_usd)

        logger.info(
            f"LLM call recorded: agent={agent_name}, tokens={prompt_tokens + completion_tokens}, cost=${cost_usd:.4f}"
        )


# Global metrics collector instance
metrics_collector = MetricsCollector()
