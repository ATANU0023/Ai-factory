"""Model routing system with fallback, rate limiting, and cost tracking."""

import time
from typing import Any, Literal

import tiktoken
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import ModelConfig, settings
from memory.semantic_cache import SemanticCache
from observability.logger import get_logger
from observability.metrics import metrics_collector

logger = get_logger(__name__)

TaskType = Literal["planning", "code", "log_analysis", "summarization"]


class ModelRouter:
    """Route requests to optimal LLM models with fallback and cost tracking."""

    def __init__(self, session_id: str, semantic_cache: SemanticCache | None = None) -> None:
        self.session_id = session_id
        self.semantic_cache = semantic_cache or SemanticCache()
        self.client = OpenAI(
            base_url=settings.openrouter_api_key and "https://openrouter.ai/api/v1" or "",
            api_key=settings.openrouter_api_key or "",
        )
        self.token_counts: dict[str, int] = {"prompt": 0, "completion": 0}

    def _is_valid_response(self, content: str, task_type: TaskType) -> bool:
        """Validate that response is appropriate for caching."""
        if not content or len(content.strip()) < 10:
            return False
        
        # For planning tasks, ensure it's JSON (not error text)
        if task_type == "planning":
            # Check if it looks like a JSON object or array
            stripped = content.strip()
            if not (stripped.startswith("{") or stripped.startswith("[")):
                # Try to extract JSON from markdown
                if "```json" in stripped:
                    return True
                logger.warning(f"Planning response doesn't look like JSON: {content[:100]}...")
                return False
        
        # For code tasks, ensure it's not an error message
        if task_type == "code":
            error_indicators = ["Error:", "Exception:", "Traceback:", "Failed:", "Cannot"]
            if any(indicator in content[:200] for indicator in error_indicators):
                logger.warning(f"Code response contains error indicators: {content[:100]}...")
                return False
        
        return True

    def _count_tokens(self, text: str, model_name: str) -> int:
        """Count tokens in text using tiktoken."""
        try:
            encoding = tiktoken.encoding_for_model(model_name.split("/")[-1])
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int, model_name: str) -> float:
        """Calculate cost in USD based on model pricing.
        
        Note: These are approximate OpenRouter prices. Adjust as needed.
        """
        # Simplified pricing (per 1M tokens)
        pricing = {
            "deepseek-chat": {"prompt": 0.14, "completion": 0.28},
            "deepseek-coder": {"prompt": 0.14, "completion": 0.28},
            "llama-3.1-8b-instruct": {"prompt": 0.05, "completion": 0.05},
            "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
        }

        model_key = model_name.split("/")[-1]
        rates = pricing.get(model_key, {"prompt": 0.50, "completion": 1.50})

        cost = (prompt_tokens * rates["prompt"] + completion_tokens * rates["completion"]) / 1_000_000
        return round(cost, 6)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
    def execute_with_fallback(self, task_type: TaskType, messages: list[dict[str, str]]) -> dict[str, Any]:
        """Execute LLM request with caching, fallback, and retry logic."""
        model_config = settings.get_model_for_task(task_type)

        # Check semantic cache first
        request_text = "\n".join([m.get("content", "") for m in messages])
        cached_result = self.semantic_cache.check_cache(request_text)

        if cached_result and cached_result.get("cache_hit"):
            logger.info("Returning cached result")
            return {
                "response": cached_result["response"],
                "cache_hit": True,
                "model": model_config.model_name,
                "tokens": {"prompt": 0, "completion": 0},
                "cost": 0.0,
            }

        # Execute LLM call
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=model_config.model_name,
                messages=messages,
                temperature=model_config.temperature,
                max_tokens=model_config.max_tokens,
                timeout=model_config.timeout,
            )

            latency = time.time() - start_time

            # Extract response
            content = response.choices[0].message.content
            usage = response.usage

            prompt_tokens = usage.prompt_tokens if usage else self._count_tokens(request_text, model_config.model_name)
            completion_tokens = usage.completion_tokens if usage else self._count_tokens(content or "", model_config.model_name)
            cost = self._calculate_cost(prompt_tokens, completion_tokens, model_config.model_name)

            # Record metrics
            metrics_collector.record_llm_call(
                session_id=self.session_id,
                agent_name=task_type,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost_usd=cost,
                latency_seconds=latency,
                success=True,
            )

            # Store in cache (only for successful, valid responses)
            if content and self._is_valid_response(content, task_type):
                self.semantic_cache.store_result(request_text, content or "", prompt_tokens, completion_tokens)
            else:
                logger.warning("Skipping cache storage for invalid response")

            logger.info(
                f"LLM call successful: model={model_config.model_name}, "
                f"tokens={prompt_tokens + completion_tokens}, cost=${cost:.6f}, "
                f"latency={latency:.2f}s"
            )

            return {
                "response": content,
                "cache_hit": False,
                "model": model_config.model_name,
                "tokens": {"prompt": prompt_tokens, "completion": completion_tokens},
                "cost": cost,
                "latency": latency,
            }

        except Exception as e:
            latency = time.time() - start_time
            logger.error(f"LLM call failed: {e}")

            # Record failed attempt
            metrics_collector.record_llm_call(
                session_id=self.session_id,
                agent_name=task_type,
                prompt_tokens=0,
                completion_tokens=0,
                cost_usd=0.0,
                latency_seconds=latency,
                success=False,
            )

            raise

    def route_request(self, task_type: TaskType, prompt: str, system_prompt: str = "") -> dict[str, Any]:
        """Route a request to the appropriate model."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        return self.execute_with_fallback(task_type, messages)

    def get_cost_estimate(self, task_type: TaskType, estimated_tokens: int) -> float:
        """Estimate cost for a given number of tokens."""
        model_config = settings.get_model_for_task(task_type)
        # Rough estimate: 50% prompt, 50% completion
        prompt_tokens = estimated_tokens // 2
        completion_tokens = estimated_tokens // 2
        return self._calculate_cost(prompt_tokens, completion_tokens, model_config.model_name)

    def check_token_limits(self) -> dict[str, bool]:
        """Check if token usage is within governance limits."""
        session = metrics_collector.get_session(self.session_id)
        if not session:
            return {"within_limits": True}

        total_tokens = session.total_token_usage.total_tokens
        cost = session.total_token_usage.cost_usd

        return {
            "within_limits": (
                total_tokens < settings.cost_governance.max_tokens_per_session
                and cost < settings.cost_governance.max_cost_per_session
            ),
            "total_tokens": total_tokens,
            "max_tokens": settings.cost_governance.max_tokens_per_session,
            "current_cost": cost,
            "max_cost": settings.cost_governance.max_cost_per_session,
        }
