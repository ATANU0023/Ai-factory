"""Safe filesystem operations with path validation."""

import os
from pathlib import Path

from config.settings import settings
from observability.logger import get_logger

logger = get_logger(__name__)


class FilesystemTools:
    """Secure file operations with directory traversal prevention."""

    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = Path(base_dir or settings.project_output_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _validate_path(self, file_path: str) -> Path:
        """Validate file path to prevent directory traversal attacks."""
        requested_path = Path(file_path)

        # If absolute path, make it relative to base_dir
        if requested_path.is_absolute():
            relative_path = requested_path.relative_to(requested_path.anchor)
        else:
            relative_path = requested_path

        full_path = (self.base_dir / relative_path).resolve()

        # Ensure path is within base directory
        if not str(full_path).startswith(str(self.base_dir)):
            raise ValueError(f"Path traversal detected: {file_path}")

        return full_path

    def create_file(self, file_path: str, content: str) -> str:
        """Create a file with validated path."""
        try:
            validated_path = self._validate_path(file_path)

            # Create parent directories if needed
            validated_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            validated_path.write_text(content, encoding="utf-8")

            logger.info(f"File created: {validated_path}")
            return str(validated_path)

        except Exception as e:
            logger.error(f"Failed to create file {file_path}: {e}")
            raise

    def read_file(self, file_path: str) -> str:
        """Read file content with validated path."""
        try:
            validated_path = self._validate_path(file_path)

            if not validated_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            content = validated_path.read_text(encoding="utf-8")
            logger.info(f"File read: {validated_path}")
            return content

        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise

    def list_directory(self, dir_path: str = ".") -> list[str]:
        """List directory contents with validated path."""
        try:
            validated_path = self._validate_path(dir_path)

            if not validated_path.is_dir():
                raise NotADirectoryError(f"Not a directory: {dir_path}")

            items = [str(item.relative_to(self.base_dir)) for item in validated_path.iterdir()]
            logger.info(f"Directory listed: {dir_path} ({len(items)} items)")
            return items

        except Exception as e:
            logger.error(f"Failed to list directory {dir_path}: {e}")
            raise

    def delete_file(self, file_path: str) -> None:
        """Delete a file with validated path."""
        try:
            validated_path = self._validate_path(file_path)

            if validated_path.exists():
                validated_path.unlink()
                logger.info(f"File deleted: {validated_path}")

        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            raise

    def file_exists(self, file_path: str) -> bool:
        """Check if file exists."""
        try:
            validated_path = self._validate_path(file_path)
            return validated_path.exists()
        except Exception:
            return False
