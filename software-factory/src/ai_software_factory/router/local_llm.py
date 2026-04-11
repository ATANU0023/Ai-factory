"""Local LLM management and inference engine."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import time



from ai_software_factory.config.settings import settings
from ai_software_factory.observability.logger import get_logger

logger = get_logger(__name__, interactive=True)

def check_local_dependencies() -> list[str]:
    """Check which optional dependencies for Local Mode are missing."""
    missing = []
    try:
        import llama_cpp
    except ImportError:
        missing.append("llama-cpp-python")
    try:
        import huggingface_hub
    except ImportError:
        missing.append("huggingface-hub")
    try:
        import tqdm
    except ImportError:
        missing.append("tqdm")
    return missing

class LocalLLMManager:
    """Manages local LLM model downloads and inference."""

    def __init__(self) -> None:
        self.model_path = Path(settings.local_model_dir) / settings.local_model_file
        self.llm = None
        self._is_initialized = False

    def is_model_downloaded(self) -> bool:
        """Check if the model file already exists on disk."""
        return self.model_path.exists()

    def download_model(self) -> bool:
        """Download the model from HuggingFace with a progress bar."""
        print("\n" + "=" * 80)
        print(f"📦 Downloading Local AI Model: {settings.local_model_repo}")
        print("This is a one-time download of ~950MB. Please wait...")
        print("=" * 80 + "\n")

        try:
            from tqdm import tqdm
            from huggingface_hub import hf_hub_download
            
            # Create directory if it doesn't exist
            os.makedirs(settings.local_model_dir, exist_ok=True)
            
            # Use huggingface_hub's hf_hub_download which handles hashing and caching
            hf_hub_download(
                repo_id=settings.local_model_repo,
                filename=settings.local_model_file,
                local_dir=settings.local_model_dir,
                local_dir_use_symlinks=False,
            )
            
            print("\n✅ Download complete!")
            return True
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            print(f"\n❌ Download failed: {e}")
            return False

    def initialize_if_needed(self) -> bool:
        """Load the model into memory if not already loaded."""
        if self._is_initialized:
            return True

        if not self.is_model_downloaded():
            logger.warning("Model not found. Download required.")
            return False

        try:
            from llama_cpp import Llama
            
            logger.info(f"Loading local model from {self.model_path}...")
            # Use physical core count for inference threads, all logical cores for batch ingestion
            logical_cores = os.cpu_count() or 4
            physical_cores = max(1, logical_cores // 2)
            
            # Initialize with high-performance CPU settings
            self.llm = Llama(
                model_path=str(self.model_path),
                n_ctx=8192,           # Larger context for complex code files
                n_batch=512,          # Standard high-speed prompt ingestion
                n_threads=physical_cores, 
                n_threads_batch=logical_cores, 
                f16_kv=True,          # Speed up memory mapping
                logits_all=False,     # Reduce compute overhead
                verbose=False         # Keep it clean
            )
            self._is_initialized = True
            logger.info("Local model loaded successfully.")
            return True
        except ImportError:
            logger.error("'llama-cpp-python' not found. Is it installed?")
            return False
        except Exception as e:
            logger.error(f"Error loading local model: {e}")
            return False

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 1024) -> Optional[Dict[str, Any]]:
        """Run local inference using llama-cpp-python."""
        if not self.initialize_if_needed():
            return None

        # Convert OpenAI-style messages to a raw prompt
        # Qwen2.5-Coder uses ChatML-like format
        prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            prompt += f"<|im_start|>{role}\n{content}<|im_end|>\n"
        prompt += "<|im_start|>assistant\n"

        try:
            start_time = time.time()
            output = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["<|im_end|>", "<|im_start|>", "assistant"],
                echo=False
            )
            latency = time.time() - start_time

            content = output["choices"][0]["text"].strip()
            
            # Mock the usage object to match OpenAI response format
            prompt_tokens = output["usage"]["prompt_tokens"]
            completion_tokens = output["usage"]["completion_tokens"]
            
            return {
                "content": content,
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                },
                "latency": latency,
                "model": f"local:{settings.local_model_repo}"
            }
        except Exception as e:
            logger.error(f"Local inference failed: {e}")
            return None
