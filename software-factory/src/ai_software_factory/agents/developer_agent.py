"""Developer Agent - Generates production code from architectural plans."""

import time
from typing import Any

from ai_software_factory.agents import BaseAgent
from ai_software_factory.observability.logger import get_logger
from ai_software_factory.observability.metrics import TokenUsage
from ai_software_factory.router.model_router import TaskType
from ai_software_factory.tools.filesystem_tools import FilesystemTools

logger = get_logger(__name__)


class CodeArtifact:
    """Represents generated code for a file."""

    def __init__(self, file_path: str, content: str) -> None:
        self.file_path = file_path
        self.content = content


class DeveloperAgent(BaseAgent):
    """Generate production-ready code based on Architect plan."""

    def __init__(self, model_router: Any, session_id: str) -> None:
        super().__init__(model_router, session_id)
        self.filesystem = FilesystemTools()

    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute code generation for all tasks."""
        start_time = time.time()

        architect_plan = state.get("architect_plan")
        if not architect_plan:
            logger.error("No architect plan found in state")
            state["error"] = "Missing architect plan"
            return state

        tasks = architect_plan.get("tasks", [])
        if not tasks:
            logger.error("No tasks in architect plan")
            state["error"] = "Empty task list"
            return state

        logger.info(f"Developer Agent starting: {len(tasks)} tasks to implement")

        generated_files = []
        total_tokens = TokenUsage()

        try:
            for task in tasks:
                task_id = task.get("task_id", "")
                description = task.get("description", "")
                files_to_create = task.get("files", [])

                logger.info(f"Generating code for task: {task_id}")

                # Generate code for each file
                for file_path in files_to_create:
                    artifact = self._generate_code_for_file(task, file_path)
                    if artifact:
                        # Create file
                        self.filesystem.create_file(artifact.file_path, artifact.content)
                        generated_files.append(artifact.file_path)
                        logger.info(f"Created file: {artifact.file_path}")

            state["generated_files"] = generated_files
            state["current_step"] = "developer_complete"

            # Record metrics
            self._record_metrics(start_time, total_tokens, True)
            logger.info(f"Developer complete: {len(generated_files)} files created")
            return state

        except Exception as e:
            logger.error(f"Developer Agent failed: {e}", exc_info=True)
            state["error"] = str(e)
            self._record_metrics(start_time, total_tokens, False)
            return state

    def _generate_code_for_file(self, task: dict[str, Any], file_path: str) -> CodeArtifact | None:
        """Generate code for a specific file."""
        system_prompt = f"""You are a Senior Software Engineer. Generate production-ready code.

RULES:
1. Write clean, modular, well-documented code
2. Include error handling and logging
3. Follow best practices for the tech stack
4. Include unit tests where appropriate
5. Use proper TypeScript/Python conventions
6. Add comprehensive comments

File to create: {file_path}
Task description: {task.get('description', '')}
Project context: {task.get('project_context', '')}

Return ONLY the file content, no explanations."""

        try:
            result = self.model_router.route_request(
                task_type="code",
                prompt=f"Generate the complete content for file: {file_path}\n\nRequirements: {task.get('description', '')}",
                system_prompt=system_prompt,
            )

            content = result.get("response", "")
            if not content:
                logger.warning(f"Empty content generated for {file_path}")
                return None

            return CodeArtifact(file_path=file_path, content=content)

        except Exception as e:
            logger.error(f"Failed to generate code for {file_path}: {e}")
            return None

    def install_dependencies(self, dependencies: list[str]) -> bool:
        """Install project dependencies."""
        logger.info(f"Installing dependencies: {dependencies}")
        # This would be handled by sandbox executor in production
        return True
