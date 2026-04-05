"""File management tools for reading, writing, editing, and diffing files."""

import difflib
from pathlib import Path
from typing import Any

from observability.logger import get_logger

logger = get_logger(__name__)


class FileManager:
    """Manage file operations with safety checks and diff preview (Claude Code-like)."""

    def __init__(self, base_dir: str = None) -> None:
        """Initialize with optional base directory (defaults to current working directory)."""
        from pathlib import Path
        
        if base_dir:
            self.base_dir = Path(base_dir).resolve()
        else:
            # Default to current working directory (like Claude Code)
            self.base_dir = Path.cwd().resolve()
        
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup system
        self.backup_dir = self.base_dir / ".ai-factory-backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Undo/redo history
        self.undo_stack = []
        self.redo_stack = []
        
        logger.info(f"FileManager initialized in: {self.base_dir}")

    def _validate_path(self, file_path: str) -> Path:
        """Validate and resolve file path (allows any path for Claude Code-like behavior)."""
        from pathlib import Path
        
        # If absolute path, use it directly
        full_path = Path(file_path)
        if not full_path.is_absolute():
            # Relative path - resolve from base_dir
            full_path = (self.base_dir / file_path).resolve()
        else:
            full_path = full_path.resolve()
        
        return full_path

    def change_directory(self, new_dir: str) -> dict[str, Any]:
        """Change working directory (like cd command)."""
        try:
            from pathlib import Path
            new_path = Path(new_dir).resolve()
            
            if not new_path.exists():
                return {
                    "success": False,
                    "message": f"Directory not found: {new_dir}",
                }
            
            if not new_path.is_dir():
                return {
                    "success": False,
                    "message": f"Not a directory: {new_dir}",
                }
            
            old_dir = self.base_dir
            self.base_dir = new_path
            
            # Recreate backup dir in new location
            self.backup_dir = self.base_dir / ".ai-factory-backups"
            self.backup_dir.mkdir(exist_ok=True)
            
            logger.info(f"Changed directory to: {new_path}")
            return {
                "success": True,
                "message": f"Changed to: {new_path}",
                "old_dir": str(old_dir),
                "new_dir": str(new_path),
            }
            
        except Exception as e:
            logger.error(f"Failed to change directory: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
            }

    def read_file(self, file_path: str) -> str:
        """Read file content."""
        try:
            full_path = self._validate_path(file_path)
            if not full_path.exists():
                logger.warning(f"File not found: {file_path}")
                return ""
            
            content = full_path.read_text(encoding="utf-8")
            logger.info(f"Read file: {file_path} ({len(content)} chars)")
            return content
            
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return ""

    def write_file(self, file_path: str, content: str, confirm: bool = True, create_backup: bool = True) -> dict[str, Any]:
        """Write content to file with optional confirmation and automatic backup."""
        try:
            full_path = self._validate_path(file_path)
            
            # Create parent directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists
            old_content = None
            if full_path.exists():
                old_content = full_path.read_text(encoding="utf-8")
                if old_content == content:
                    return {
                        "success": True,
                        "message": "No changes needed - file already has this content",
                        "action": "unchanged",
                    }
                
                # Create backup before modifying
                if create_backup:
                    self._create_backup(full_path, old_content)
                
                # Show diff if file will be modified
                if confirm:
                    diff = self._generate_diff(old_content, content, file_path)
                    return {
                        "success": False,
                        "message": "File exists and will be modified",
                        "action": "needs_confirmation",
                        "diff": diff,
                        "old_size": len(old_content),
                        "new_size": len(content),
                    }
            
            # Write the file
            full_path.write_text(content, encoding="utf-8")
            logger.info(f"Written file: {file_path} ({len(content)} chars)")
            
            # Track for undo
            if old_content is not None:
                self.undo_stack.append({
                    "action": "write",
                    "file": str(full_path),
                    "old_content": old_content,
                    "new_content": content,
                })
                self.redo_stack.clear()  # Clear redo on new action
            
            return {
                "success": True,
                "message": f"File written successfully: {file_path}",
                "action": "created" if old_content is None else "updated",
                "size": len(content),
            }
            
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "action": "failed",
            }

    def edit_file(
        self,
        file_path: str,
        search_text: str,
        replace_text: str,
        replace_all: bool = False,
    ) -> dict[str, Any]:
        """Edit file by replacing text (like search & replace)."""
        try:
            full_path = self._validate_path(file_path)
            
            if not full_path.exists():
                return {
                    "success": False,
                    "message": f"File not found: {file_path}",
                    "action": "failed",
                }
            
            content = full_path.read_text(encoding="utf-8")
            
            # Count occurrences
            count = content.count(search_text)
            if count == 0:
                return {
                    "success": False,
                    "message": f"Search text not found in {file_path}",
                    "action": "not_found",
                }
            
            # Perform replacement
            if replace_all:
                new_content = content.replace(search_text, replace_text)
            else:
                new_content = content.replace(search_text, replace_text, 1)
            
            # Generate diff
            diff = self._generate_diff(content, new_content, file_path)
            
            return {
                "success": True,
                "message": f"Found {count} occurrence(s)",
                "action": "preview_ready",
                "diff": diff,
                "occurrences": count,
                "old_content": content,
                "new_content": new_content,
            }
            
        except Exception as e:
            logger.error(f"Failed to edit file {file_path}: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "action": "failed",
            }

    def apply_edit(self, file_path: str, new_content: str) -> dict[str, Any]:
        """Apply edited content to file."""
        try:
            full_path = self._validate_path(file_path)
            full_path.write_text(new_content, encoding="utf-8")
            
            logger.info(f"Applied edit to: {file_path}")
            return {
                "success": True,
                "message": f"Changes applied to {file_path}",
                "action": "applied",
            }
            
        except Exception as e:
            logger.error(f"Failed to apply edit to {file_path}: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "action": "failed",
            }

    def list_files(self, directory: str = "") -> list[str]:
        """List files in directory."""
        try:
            dir_path = self._validate_path(directory) if directory else self.base_dir
            
            if not dir_path.exists():
                return []
            
            files = []
            for item in dir_path.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(self.base_dir)
                    files.append(str(rel_path))
            
            logger.info(f"Listed {len(files)} files in {directory or 'root'}")
            return sorted(files)
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []

    def delete_file(self, file_path: str, confirm: bool = True) -> dict[str, Any]:
        """Delete a file with confirmation."""
        try:
            full_path = self._validate_path(file_path)
            
            if not full_path.exists():
                return {
                    "success": False,
                    "message": f"File not found: {file_path}",
                    "action": "not_found",
                }
            
            if confirm:
                return {
                    "success": False,
                    "message": f"Ready to delete: {file_path}",
                    "action": "needs_confirmation",
                    "size": full_path.stat().st_size,
                }
            
            full_path.unlink()
            logger.info(f"Deleted file: {file_path}")
            
            return {
                "success": True,
                "message": f"Deleted: {file_path}",
                "action": "deleted",
            }
            
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "action": "failed",
            }

    def _generate_diff(self, old_content: str, new_content: str, filename: str) -> str:
        """Generate unified diff between old and new content."""
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
            lineterm="",
        )
        
        return "".join(diff)

    def get_file_info(self, file_path: str) -> dict[str, Any]:
        """Get file metadata."""
        try:
            full_path = self._validate_path(file_path)
            
            if not full_path.exists():
                return {"exists": False}
            
            stat = full_path.stat()
            return {
                "exists": True,
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "is_file": full_path.is_file(),
                "is_directory": full_path.is_dir(),
            }
            
        except Exception as e:
            logger.error(f"Failed to get file info: {e}")
            return {"exists": False, "error": str(e)}

    def _create_backup(self, file_path: Path, content: str) -> str:
        """Create backup of file before modification."""
        import time
        from pathlib import Path
        
        timestamp = int(time.time())
        rel_path = file_path.relative_to(self.base_dir) if file_path.is_relative_to(self.base_dir) else file_path.name
        backup_name = f"{rel_path}.{timestamp}.bak"
        
        # Sanitize backup name (replace path separators)
        backup_name = str(backup_name).replace("\\", "_").replace("/", "_")
        backup_path = self.backup_dir / backup_name
        
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        backup_path.write_text(content, encoding="utf-8")
        
        logger.info(f"Created backup: {backup_path}")
        return str(backup_path)

    def undo(self) -> dict[str, Any]:
        """Undo last file operation."""
        if not self.undo_stack:
            return {
                "success": False,
                "message": "Nothing to undo",
            }
        
        last_action = self.undo_stack.pop()
        
        try:
            if last_action["action"] == "write":
                file_path = Path(last_action["file"])
                old_content = last_action["old_content"]
                
                # Save current state for redo
                current_content = file_path.read_text(encoding="utf-8") if file_path.exists() else None
                self.redo_stack.append({
                    **last_action,
                    "current_content": current_content,
                })
                
                # Restore old content
                if old_content is not None:
                    file_path.write_text(old_content, encoding="utf-8")
                    logger.info(f"Undid write to: {file_path}")
                    return {
                        "success": True,
                        "message": f"Undid changes to {file_path.name}",
                        "file": str(file_path),
                    }
                else:
                    # File was created, delete it
                    file_path.unlink()
                    logger.info(f"Unded creation of: {file_path}")
                    return {
                        "success": True,
                        "message": f"Removed newly created file: {file_path.name}",
                        "file": str(file_path),
                    }
            
            return {
                "success": False,
                "message": "Unknown action type",
            }
            
        except Exception as e:
            logger.error(f"Failed to undo: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
            }

    def redo(self) -> dict[str, Any]:
        """Redo last undone operation."""
        if not self.redo_stack:
            return {
                "success": False,
                "message": "Nothing to redo",
            }
        
        last_redo = self.redo_stack.pop()
        
        try:
            if last_redo["action"] == "write":
                file_path = Path(last_redo["file"])
                new_content = last_redo["new_content"]
                
                # Save current state for undo
                current_content = file_path.read_text(encoding="utf-8") if file_path.exists() else None
                self.undo_stack.append({
                    **last_redo,
                    "old_content": current_content,
                })
                
                # Restore new content
                file_path.write_text(new_content, encoding="utf-8")
                logger.info(f"Redid write to: {file_path}")
                return {
                    "success": True,
                    "message": f"Redid changes to {file_path.name}",
                    "file": str(file_path),
                }
            
            return {
                "success": False,
                "message": "Unknown action type",
            }
            
        except Exception as e:
            logger.error(f"Failed to redo: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
            }

    def list_backups(self) -> list[str]:
        """List all backup files."""
        if not self.backup_dir.exists():
            return []
        
        backups = []
        for backup_file in self.backup_dir.rglob("*.bak"):
            rel_path = backup_file.relative_to(self.backup_dir)
            backups.append(str(rel_path))
        
        return sorted(backups)

    def restore_backup(self, backup_name: str) -> dict[str, Any]:
        """Restore a specific backup file."""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            return {
                "success": False,
                "message": f"Backup not found: {backup_name}",
            }
        
        try:
            # Extract original filename (remove .timestamp.bak)
            parts = backup_name.rsplit(".", 2)
            if len(parts) >= 3:
                original_name = parts[0]
            else:
                original_name = backup_name.replace(".bak", "")
            
            # Restore to original location
            original_path = self.base_dir / original_name
            backup_content = backup_path.read_text(encoding="utf-8")
            original_path.write_text(backup_content, encoding="utf-8")
            
            logger.info(f"Restored backup: {backup_name} -> {original_path}")
            return {
                "success": True,
                "message": f"Restored {original_name} from backup",
                "file": str(original_path),
            }
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
            }


