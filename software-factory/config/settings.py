"""Configuration management for the Autonomous AI Software Factory."""

from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ModelConfig(BaseSettings):
    """Configuration for a specific LLM model."""

    model_name: str
    api_base: str = "https://openrouter.ai/api/v1"
    timeout: int = 60
    max_retries: int = 3
    temperature: float = 0.7
    max_tokens: int = 4096


class CostGovernanceConfig(BaseSettings):
    """Cost governance thresholds."""

    max_tokens_per_task: int = 200000
    max_tokens_per_agent: int = 50000
    max_tokens_per_session: int = 500000
    max_cost_per_session: float = 10.0  # USD
    semantic_cache_threshold: float = 0.85


class SandboxConfig(BaseSettings):
    """Docker sandbox configuration."""

    cpu_limit: float = 2.0
    memory_limit: str = "2g"
    network_mode: str = "restricted"
    allowed_networks: list[str] = Field(
        default_factory=lambda: ["registry.npmjs.org", "pypi.org", "files.pythonhosted.org"]
    )
    blocked_paths: list[str] = Field(
        default_factory=lambda: ["/.env", "/.ssh", "/etc/shadow", "/root"]
    )
    execution_timeout: int = 300
    container_image: str = "software-factory-sandbox:latest"


class QdrantConfig(BaseSettings):
    """Qdrant vector database configuration."""

    host: str = "localhost"
    port: int = 6333
    api_key: str | None = None  # For Qdrant Cloud
    collection_prefix: str = "software_factory"
    vector_size: int = 1536
    distance: str = "Cosine"
    use_cloud: bool = False  # Set to True for Qdrant Cloud


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # API Keys
    openrouter_api_key: str = Field(..., description="OpenRouter API key")

    # Model configurations
    planning_model: ModelConfig = Field(
        default_factory=lambda: ModelConfig(
            model_name="deepseek/deepseek-chat",
            max_tokens=8192,
            temperature=0.3,
        )
    )
    code_generation_model: ModelConfig = Field(
        default_factory=lambda: ModelConfig(
            model_name="deepseek/deepseek-chat",  # Use deepseek-chat for code (coder model may not be available)
            max_tokens=8192,
            temperature=0.2,
        )
    )
    log_analysis_model: ModelConfig = Field(
        default_factory=lambda: ModelConfig(
            model_name="meta-llama/llama-3.1-8b-instruct",
            max_tokens=2048,
            temperature=0.1,
        )
    )
    summarization_model: ModelConfig = Field(
        default_factory=lambda: ModelConfig(
            model_name="openai/gpt-4o-mini",
            max_tokens=2048,
            temperature=0.3,
        )
    )

    # Component configurations
    cost_governance: CostGovernanceConfig = Field(default_factory=CostGovernanceConfig)
    sandbox: SandboxConfig = Field(default_factory=SandboxConfig)
    qdrant: QdrantConfig = Field(default_factory=QdrantConfig)

    # Application settings
    debug: bool = False
    log_level: str = "INFO"
    project_output_dir: str = "./output"
    
    # Vector database configuration
    vector_db_type: str = "qdrant"  # Options: "qdrant" or "chromadb"
    chroma_db_path: str = "./chroma_db"  # Path for ChromaDB storage

    def get_model_for_task(self, task_type: Literal["planning", "code", "log_analysis", "summarization"]) -> ModelConfig:
        """Get model configuration for a specific task type."""
        model_map = {
            "planning": self.planning_model,
            "code": self.code_generation_model,
            "log_analysis": self.log_analysis_model,
            "summarization": self.summarization_model,
        }
        return model_map[task_type]


# Global settings instance
settings = Settings()
