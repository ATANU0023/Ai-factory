"""Architect Agent - Designs system architecture from user requirements."""

import json
import time
from typing import Any

from agents import ArchitectPlan, BaseAgent
from observability.logger import get_logger
from observability.metrics import TokenUsage
from router.model_router import TaskType

logger = get_logger(__name__)


class ArchitectAgent(BaseAgent):
    """Parse user requirements and design system architecture."""

    def _force_fresh_llm_call(self, user_input: str, system_prompt: str) -> dict:
        """Force a fresh LLM call bypassing cache."""
        logger.info("Making fresh LLM call (bypassing cache)...")
        from openai import OpenAI
        from config.settings import settings
        
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
        )
        
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.3,
            max_tokens=8192,
        )
        
        content = response.choices[0].message.content or ""
        return {
            "response": content,
            "cache_hit": False,
            "model": "deepseek/deepseek-chat",
            "tokens": {"prompt": 0, "completion": 0},
            "cost": 0.0,
        }

    def generate_clarifying_questions(self, user_input: str) -> list[str]:
        """Generate clarifying questions based on user requirements."""
        
        # First, check if this is actually a project request
        if not self._is_project_request(user_input):
            logger.info("Input is not a project request, skipping questions")
            return []
        
        logger.info("Generating clarifying questions...")
        
        question_prompt = f"""Based on this project request, generate 3-5 clarifying questions to better understand the requirements.

Project Request: {user_input}

Return ONLY a JSON array of questions like:
["What framework should I use?", "Do you need authentication?"]

Rules:
1. Ask about technology choices (frameworks, languages, databases)
2. Ask about key features and scope
3. Ask about deployment preferences
4. Keep questions concise and specific
5. Return valid JSON only"""

        try:
            result = self.model_router.route_request(
                task_type="planning",
                prompt=question_prompt,
                system_prompt="You are a helpful assistant that asks clarifying questions.",
            )
            
            response_text = result.get("response", "[]")
            
            # Parse JSON
            import json
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            questions = json.loads(response_text)
            
            if isinstance(questions, list) and len(questions) > 0:
                logger.info(f"Generated {len(questions)} clarifying questions")
                return questions[:5]  # Limit to 5 questions max
            else:
                logger.warning("Invalid questions format, using defaults")
                return self._default_questions()
                
        except Exception as e:
            logger.error(f"Failed to generate questions: {e}")
            return self._default_questions()

    def _is_project_request(self, user_input: str) -> bool:
        """Determine if input is a project request or just casual conversation."""
        text = user_input.lower().strip()
        
        # Casual greetings/conversation patterns
        casual_patterns = [
            "hi", "hello", "hey", "greetings", "howdy",
            "how are you", "whats up", "what's up",
            "thank", "thanks", "bye", "goodbye",
            "test", "testing", "help",
        ]
        
        # Check if it's just a greeting or casual chat
        if any(pattern in text for pattern in casual_patterns):
            # But allow if it also contains project keywords
            project_keywords = [
                "create", "build", "make", "develop", "design",
                "app", "application", "website", "api", "system",
                "program", "software", "tool", "service",
                "python", "javascript", "flask", "react", "node",
            ]
            
            has_project_keyword = any(keyword in text for keyword in project_keywords)
            if not has_project_keyword:
                return False
        
        # Check for project-related action verbs
        project_verbs = [
            "create", "build", "make", "develop", "design",
            "implement", "code", "write", "generate",
        ]
        
        has_verb = any(verb in text for verb in project_verbs)
        
        # Check for project nouns
        project_nouns = [
            "app", "application", "website", "api", "system",
            "program", "software", "tool", "service", "platform",
            "dashboard", "portal", "interface",
        ]
        
        has_noun = any(noun in text for noun in project_nouns)
        
        # It's a project request if it has both verb+noun or is clearly descriptive
        if has_verb and has_noun:
            return True
        
        # Also accept descriptive requests like "a todo list manager"
        if len(text.split()) >= 3 and not any(pattern in text for pattern in casual_patterns[:5]):
            return True
        
        return False

    def _default_questions(self) -> list[str]:
        """Return default clarifying questions."""
        return [
            "What programming language/framework do you prefer?",
            "Do you need database support? If yes, which type?",
            "Should this include authentication/authorization?",
            "Is this for web, mobile, or desktop?",
            "Any specific libraries or tools you want to use?",
        ]

    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute architectural planning."""
        start_time = time.time()
        user_input = state.get("user_input", "")
        clarifications = state.get("clarifications", {})

        if not user_input:
            logger.error("No user input provided to Architect Agent")
            state["error"] = "Missing user input"
            return state

        logger.info(f"Architect Agent processing: {user_input[:100]}...")

        # Build enhanced prompt with clarifications
        enhanced_input = user_input
        if clarifications:
            enhanced_input += "\n\nAdditional Context from User:\n"
            for question, answer in clarifications.items():
                enhanced_input += f"- {question}: {answer}\n"

        system_prompt = """You are a Principal Software Architect. Analyze user requirements and create a detailed development plan.

RULES:
1. Do NOT generate implementation code
2. Output MUST be valid JSON matching the schema
3. Be specific about tech stack choices
4. Break down into clear, actionable tasks
5. Define file structure explicitly
6. Include database schemas if needed

Output format (JSON):
{
  "project_name": "string",
  "tech_stack": ["list of technologies"],
  "architecture": "monolith|microservices|serverless",
  "services": [{"name": "string", "description": "string", "endpoints": []}],
  "database_schema": [{"table": "string", "columns": [{"name": "string", "type": "string"}]}],
  "tasks": [
    {
      "task_id": "unique_id",
      "description": "what to build",
      "files": ["file paths to create"],
      "dependencies": ["task_ids this depends on"]
    }
  ]
}"""

        try:
            result = self.model_router.route_request(
                task_type="planning",
                prompt=enhanced_input,
                system_prompt=system_prompt,
            )

            # Parse JSON response
            response_text = result.get("response", "{}")
            
            # Check if this is a cache hit with invalid data
            if result.get("cache_hit"):
                logger.info(f"Cache hit for architect - validating response...")
                # If cached response doesn't look like valid planning output, ignore it
                stripped = response_text.strip()
                if not (stripped.startswith("{") or stripped.startswith("[") or "```json" in stripped):
                    logger.warning("Cached architect response is invalid JSON, ignoring cache")
                    # Force a fresh LLM call by calling again without cache
                    result = self._force_fresh_llm_call(user_input, system_prompt)
                    response_text = result.get("response", "{}")
            
            logger.info(f"Raw LLM response (first 500 chars): {response_text[:500]}")
            
            try:
                # Try to extract JSON if it's wrapped in markdown code blocks
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                plan_data = json.loads(response_text)
                plan = ArchitectPlan(**plan_data)
                logger.info(f"Successfully parsed architect plan: {plan.project_name}")
            except (json.JSONDecodeError, Exception) as e:
                logger.error(f"Failed to parse architect plan: {e}")
                logger.error(f"Response was: {response_text[:200]}")
                
                # If this was a cache hit, try one more time with fresh LLM call
                if result.get("cache_hit"):
                    logger.info("Cache provided invalid data, trying fresh LLM call...")
                    result = self._force_fresh_llm_call(user_input, system_prompt)
                    response_text = result.get("response", "{}")
                    
                    # Try parsing again
                    try:
                        if "```json" in response_text:
                            response_text = response_text.split("```json")[1].split("```")[0].strip()
                        elif "```" in response_text:
                            response_text = response_text.split("```")[1].split("```")[0].strip()
                        
                        plan_data = json.loads(response_text)
                        plan = ArchitectPlan(**plan_data)
                        logger.info(f"Successfully parsed architect plan on retry: {plan.project_name}")
                    except Exception as retry_error:
                        logger.error(f"Fresh LLM call also failed: {retry_error}")
                        state["error"] = f"Architect failed after cache miss retry: {retry_error}"
                        state["current_step"] = "architect_failed"
                        state["final_status"] = "failed"
                        self._record_metrics(start_time, TokenUsage(prompt_tokens=0, completion_tokens=0, cost_usd=0.0), False)
                        return state
                else:
                    state["error"] = f"Invalid architect output: {e}"
                    state["current_step"] = "architect_failed"
                    state["final_status"] = "failed"
                    self._record_metrics(start_time, TokenUsage(prompt_tokens=0, completion_tokens=0, cost_usd=0.0), False)
                    return state

            # Validate plan
            if not self._validate_output(plan):
                state["error"] = "Architect plan validation failed"
                self._record_metrics(
                    start_time,
                    TokenUsage(prompt_tokens=0, completion_tokens=0, cost_usd=0.0),
                    False,
                )
                return state

            # Update state
            state["architect_plan"] = plan.model_dump()
            state["current_step"] = "architect_complete"

            # Record metrics
            tokens = TokenUsage(
                prompt_tokens=result.get("tokens", {}).get("prompt", 0),
                completion_tokens=result.get("tokens", {}).get("completion", 0),
                cost_usd=result.get("cost", 0.0),
            )
            self._record_metrics(start_time, tokens, True)

            logger.info(f"Architect plan created: {len(plan.tasks)} tasks defined")
            return state

        except Exception as e:
            logger.error(f"Architect Agent failed: {e}", exc_info=True)
            state["error"] = str(e)
            self._record_metrics(
                start_time,
                TokenUsage(prompt_tokens=0, completion_tokens=0, cost_usd=0.0),
                False,
            )
            return state
