"""Sandbox execution - supports both Docker and local execution."""

import tempfile
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from config.settings import settings
from observability.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ExecutionResult:
    """Result of command execution in sandbox."""

    stdout: str
    stderr: str
    exit_code: int


class SandboxExecutor:
    """Execute code with optional Docker isolation."""

    def __init__(self, use_docker: bool = False) -> None:
        self.use_docker = use_docker
        self.container = None
        
        # Use output directory instead of temp for better Windows compatibility
        from pathlib import Path
        output_dir = Path("./output/sandbox")
        output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = str(output_dir / f"sandbox_{id(self)}")
        Path(self.temp_dir).mkdir(exist_ok=True)
        
        if self.use_docker:
            try:
                import docker
                from docker.types import LogConfig
                self.docker_client = docker.from_env()
                logger.info("Docker sandbox enabled")
            except Exception as e:
                logger.warning(f"Docker not available, falling back to local execution: {e}")
                self.use_docker = False
        else:
            logger.info("Using local execution mode (no Docker)")

    def execute_command(self, command: str, timeout: int | None = None) -> ExecutionResult:
        """Execute a command (in Docker if available, otherwise locally)."""
        exec_timeout = timeout or getattr(settings.sandbox, 'execution_timeout', 300)
        
        if self.use_docker and self.container:
            return self._execute_in_docker(command, exec_timeout)
        else:
            return self._execute_locally(command, exec_timeout)

    def _execute_in_docker(self, command: str, timeout: int) -> ExecutionResult:
        """Execute command inside Docker container."""
        try:
            exec_result = self.container.exec_run(
                cmd=["/bin/sh", "-c", command],
                demux=True,
                workdir="/workspace",
            )

            exit_code = exec_result.exit_code
            stdout = exec_result.output[0].decode("utf-8", errors="replace") if exec_result.output[0] else ""
            stderr = exec_result.output[1].decode("utf-8", errors="replace") if exec_result.output[1] else ""

            return ExecutionResult(stdout=stdout, stderr=stderr, exit_code=exit_code)

        except Exception as e:
            logger.error(f"Docker execution failed: {e}")
            return ExecutionResult(stdout="", stderr=str(e), exit_code=-1)

    def _execute_locally(self, command: str, timeout: int) -> ExecutionResult:
        """Execute command locally without Docker."""
        try:
            logger.info(f"Executing locally: {command[:50]}")
            
            # Use absolute path for Windows compatibility
            from pathlib import Path
            cwd_path = Path(self.temp_dir).resolve()
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(cwd_path),
            )

            return ExecutionResult(
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
            )

        except subprocess.TimeoutExpired:
            return ExecutionResult(
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                exit_code=-1,
            )
        except Exception as e:
            logger.error(f"Local execution failed: {e}")
            # Return empty result instead of crashing
            return ExecutionResult(stdout="", stderr=f"Execution error: {str(e)}", exit_code=-1)

    def _create_container(self) -> None:
        """Create a Docker container (only if Docker is available)."""
        if not self.use_docker:
            return
            
        try:
            from docker.types import LogConfig
            
            mem_limit = getattr(settings.sandbox, 'memory_limit', '2g')
            
            self.container = self.docker_client.containers.run(
                image=getattr(settings.sandbox, 'container_image', 'python:3.11-slim'),
                detach=True,
                tty=True,
                mem_limit=mem_limit,
                network_mode="none",
                read_only=True,
                tmpfs={"/tmp": "rw,noexec,nosuid,size=100m"},
                cap_drop=["ALL"],
                security_opt=["no-new-privileges:true"],
                volumes={self.temp_dir: {"bind": "/workspace", "mode": "rw"}},
                working_dir="/workspace",
            )
            logger.info(f"Docker container created: {self.container.short_id}")

        except Exception as e:
            logger.error(f"Failed to create Docker container: {e}")
            self.use_docker = False

    def copy_files_to_sandbox(self, files: dict[str, str] | list[str]) -> None:
        """Copy files into the sandbox (or local temp directory)."""
        if isinstance(files, list):
            logger.info(f"Files ready: {len(files)} files")
            return

        # Write files to temp directory
        for file_path, content in files.items():
            full_path = Path(self.temp_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")

        logger.info(f"Copied {len(files)} files to {self.temp_dir}")

    def copy_files_from_sandbox(self, paths: list[str]) -> dict[str, str]:
        """Copy files from sandbox (or local temp directory)."""
        results = {}

        for path in paths:
            full_path = Path(self.temp_dir) / path
            if full_path.exists():
                results[path] = full_path.read_text(encoding="utf-8")
            else:
                logger.warning(f"File not found: {path}")

        return results

    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            if self.use_docker and self.container:
                self.container.stop(timeout=5)
                self.container.remove(force=True)
                logger.info(f"Docker container cleaned up: {self.container.short_id}")
                self.container = None

            # Clean temp directory
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    def __enter__(self) -> "SandboxExecutor":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with cleanup."""
        self.cleanup()
