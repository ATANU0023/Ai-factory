"""Semantic cache to reduce LLM token usage by caching similar requests."""

import hashlib
import time
from typing import Any

from ai_software_factory.config.settings import settings
from ai_software_factory.memory.vector_store import VectorStore
from ai_software_factory.observability.logger import get_logger

logger = get_logger(__name__)


class SemanticCache:
    """Cache LLM responses based on semantic similarity."""

    def __init__(self, vector_store: VectorStore | None = None) -> None:
        # Auto-detect and use appropriate vector store
        self.vector_store = None
        if vector_store:
            self.vector_store = vector_store
        else:
            vector_db_type = getattr(settings, 'vector_db_type', 'chromadb')

            if vector_db_type == 'chromadb':
                try:
                    from ai_software_factory.memory.chromadb_store import ChromaDBStore
                    self.vector_store = ChromaDBStore()
                    logger.info("Using ChromaDB for semantic cache")
                except Exception as e:
                    logger.warning(f"ChromaDB unavailable, running without cache: {e}")
            else:
                try:
                    self.vector_store = VectorStore()
                    logger.info("Using Qdrant for semantic cache")
                except Exception as e:
                    logger.warning(f"Qdrant unavailable, running without cache: {e}")
        
        self.threshold = settings.cost_governance.semantic_cache_threshold
        self.cache_ttl = 3600  # 1 hour TTL
        self.collection_type = "code_summaries"  # Reuse code_summaries for cache

    def _generate_query_vector(self, text: str) -> list[float]:
        """Generate embedding vector for text.
        
        Note: In production, use a proper embedding model.
        For now, using a simple hash-based placeholder.
        """
        # TODO: Replace with actual embedding model (e.g., sentence-transformers)
        # This is a placeholder that creates a deterministic vector from text
        hash_value = hashlib.sha256(text.encode()).hexdigest()
        # Create a pseudo-vector from hash (in production, use real embeddings)
        vector = [float(int(hash_value[i : i + 2], 16)) / 255.0 for i in range(0, 32, 2)]
        # Pad to vector_size
        vector.extend([0.0] * (settings.qdrant.vector_size - len(vector)))
        return vector[: settings.qdrant.vector_size]

    def check_cache(self, request_text: str) -> dict[str, Any] | None:
        """Check if a similar request exists in cache."""
        if not self.vector_store:
            return None
        try:
            query_vector = self._generate_query_vector(request_text)

            results = self.vector_store.search_similar(
                collection_type=self.collection_type,
                query_vector=query_vector,
                limit=1,
                score_threshold=self.threshold,
            )

            if results:
                cached_result = results[0]
                metadata = cached_result.get("metadata", {})

                # Check TTL
                cached_time = metadata.get("cached_at", 0)
                if time.time() - cached_time > self.cache_ttl:
                    logger.info("Cache entry expired")
                    return None

                logger.info(
                    f"Cache hit! Similarity: {cached_result['score']:.2f}, "
                    f"Saving ~{metadata.get('tokens_saved', 0)} tokens"
                )

                return {
                    "response": metadata.get("response"),
                    "similarity_score": cached_result["score"],
                    "cache_hit": True,
                }

            logger.info("Cache miss - proceeding to LLM")
            return None

        except Exception as e:
            logger.error(f"Cache check failed: {e}")
            return None

    def store_result(
        self,
        request_text: str,
        response: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> None:
        """Store LLM result in cache."""
        if not self.vector_store:
            return
        try:
            query_vector = self._generate_query_vector(request_text)
            total_tokens = prompt_tokens + completion_tokens

            metadata = {
                "response": response,
                "cached_at": time.time(),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "tokens_saved": total_tokens,  # Future requests will save this
            }

            self.vector_store.store_embedding(
                collection_type=self.collection_type,
                text=request_text,
                vector=query_vector,
                metadata=metadata,
            )

            logger.info(f"Stored result in cache: {total_tokens} tokens")

        except Exception as e:
            logger.error(f"Failed to store result in cache: {e}")

    def invalidate(self, request_text: str) -> None:
        """Invalidate cache entry for a specific request."""
        # In production, implement proper deletion logic
        logger.info(f"Cache invalidation requested for: {request_text[:50]}...")

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        try:
            stats = self.vector_store.get_collection_stats(self.collection_type)
            return {
                "collection_type": self.collection_type,
                "threshold": self.threshold,
                "ttl_seconds": self.cache_ttl,
                **stats,
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}
