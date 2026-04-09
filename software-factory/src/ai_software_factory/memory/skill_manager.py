"""Skill manager for loading and injecting skills into agent prompts."""

from pathlib import Path
from ai_software_factory.observability.logger import get_logger

logger = get_logger(__name__)

class SkillManager:
    """Manages dynamic skills loaded from markdown files."""
    
    def __init__(self, skills_dir: str = "./skills"):
        self.skills_dir = Path(skills_dir)
        # Ensure the skills directory exists
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        
    def get_all_skills_text(self) -> str:
        """Read all skill files and return them as a concatenated string."""
        if not self.skills_dir.exists():
            return ""
            
        skills_text = []
        try:
            # Load all markdown files in the skills directory
            for file_path in sorted(self.skills_dir.glob("*.md")):
                if file_path.name.lower() == "readme.md":
                    continue
                    
                try:
                    content = file_path.read_text(encoding="utf-8")
                    name = file_path.stem.replace("_", " ").title()
                    skills_text.append(f"--- SKILL: {name} ---\n{content}\n")
                except Exception as e:
                    logger.error(f"Failed to load skill file {file_path}: {e}")
                    
            if skills_text:
                return "\n\nAVAILABLE SKILLS:\nThe following skills have been dynamically loaded to enhance your capabilities:\n\n" + "\n".join(skills_text)
        except Exception as e:
            logger.error(f"Error accessing skills directory: {e}")
            
        return ""
