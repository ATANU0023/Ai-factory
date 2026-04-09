"""Log summarization using LLM for concise error analysis."""

from ai_software_factory.router.model_router import ModelRouter, TaskType
from ai_software_factory.observability.logger import get_logger

logger = get_logger(__name__)


class LogSummarizer:
    """Compress and summarize verbose logs using LLM."""

    def __init__(self, model_router: ModelRouter) -> None:
        self.model_router = model_router

    def summarize(self, logs: str, max_length: int = 500) -> str:
        """Summarize verbose logs into key information."""
        if len(logs) <= max_length:
            return logs

        system_prompt = """You are a Log Analysis Expert. Summarize error logs concisely.

Extract:
1. Key error messages
2. Stack trace highlights (first and last frames)
3. Root cause indicators
4. Actionable information

Keep summary under 500 characters. Be precise and technical."""

        try:
            result = self.model_router.route_request(
                task_type="summarization",
                prompt=f"Summarize these logs:\n\n{logs[:2000]}",  # Limit input
                system_prompt=system_prompt,
            )

            summary = result.get("response", "")
            logger.info(f"Logs summarized: {len(logs)} -> {len(summary)} chars")
            return summary

        except Exception as e:
            logger.error(f"Log summarization failed: {e}")
            # Return truncated original as fallback
            return logs[:max_length] + "\n...[truncated]"

    def extract_errors(self, logs: str) -> list[str]:
        """Extract specific error messages from logs."""
        errors = []
        for line in logs.split("\n"):
            if any(keyword in line.lower() for keyword in ["error", "exception", "failed", "traceback"]):
                errors.append(line.strip())

        return errors[:10]  # Limit to first 10 errors
