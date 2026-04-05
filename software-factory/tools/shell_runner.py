"""Shell command execution with security restrictions."""

import subprocess
from typing import Literal

from config.settings import settings
from observability.logger import get_logger

logger = get_logger(__name__)


# Whitelist of allowed commands
ALLOWED_COMMANDS = {
    "npm",
    "pip",
    "python",
    "node",
    "npx",
    "pytest",
    "black",
    "ruff",
    "mypy",
    "echo",
    "cat",
    "ls",
    "pwd",
}

# Blocked commands
BLOCKED_COMMANDS = {
    "rm",
    "sudo",
    "chmod",
    "chown",
    "curl",
    "wget",
    "ssh",
    "scp",
    "eval",
    "exec",
}


class ShellRunner:
    """Execute shell commands with security restrictions."""

    def __init__(self) -> None:
        self.allowed_commands = ALLOWED_COMMANDS
        self.blocked_commands = BLOCKED_COMMANDS

    def execute(
        self,
        command: str,
        timeout: int = 30,
        working_dir: str | None = None,
    ) -> dict[str, str | int]:
        """Execute a shell command with security checks."""
        # Security validation
        self._validate_command(command)

        try:
            logger.info(f"Executing command: {command}")

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=working_dir,
                env=self._safe_environment(),
            )

            output = {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
            }

            if result.returncode == 0:
                logger.info(f"Command succeeded: {command[:50]}")
            else:
                logger.warning(f"Command failed (exit {result.returncode}): {command[:50]}")

            return output

        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            return {
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "exit_code": -1,
            }
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
            }

    def _validate_command(self, command: str) -> None:
        """Validate command against security policies."""
        # Extract base command
        base_command = command.split()[0].lower()

        # Check if command is blocked
        if base_command in self.blocked_commands:
            raise ValueError(f"Blocked command: {base_command}")

        # Check if command is allowed (if whitelist is enforced)
        if base_command not in self.allowed_commands:
            logger.warning(f"Command not in whitelist: {base_command}")
            # In strict mode, this would raise an error
            # raise ValueError(f"Command not allowed: {base_command}")

        # Check for dangerous patterns
        dangerous_patterns = [";", "&&", "|", "`", "$(", ">", ">>"]
        for pattern in dangerous_patterns:
            if pattern in command:
                logger.warning(f"Dangerous pattern detected: {pattern}")

    def _safe_environment(self) -> dict[str, str]:
        """Create a safe environment for command execution."""
        # Start with minimal environment
        safe_env = {
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "HOME": "/tmp",
            "NODE_ENV": "production",
            "PYTHONUNBUFFERED": "1",
        }

        # Add necessary environment variables
        if settings.openrouter_api_key:
            safe_env["OPENROUTER_API_KEY"] = settings.openrouter_api_key

        return safe_env
