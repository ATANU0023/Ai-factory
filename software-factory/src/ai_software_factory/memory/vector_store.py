"""Vector store implementation using Qdrant for semantic memory."""

import uuid
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models

from ai_software_factory.config.settings import settings
from ai_software_factory.observability.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """Qdrant-based vector store for semantic memory."""

    def __init__(self) -> None:
        # Support both Qdrant Cloud and local instances
        if settings.qdrant.use_cloud or settings.qdrant.api_key:
            # Qdrant Cloud configuration
            self.client = QdrantClient(
                url=settings.qdrant.host,
                api_key=settings.qdrant.api_key,
            )
            logger.info("Using Qdrant Cloud")
        else:
            # Local Qdrant instance
            self.client = QdrantClient(
                host=settings.qdrant.host,
                port=settings.qdrant.port,
            )
            logger.info(f"Using local Qdrant at {settings.qdrant.host}:{settings.qdrant.port}")
        
        self.collections = {
            "code_summaries": f"{settings.qdrant.collection_prefix}_code_summaries",
            "debug_fixes": f"{settings.qdrant.collection_prefix}_debug_fixes",
            "architecture_patterns": f"{settings.qdrant.collection_prefix}_architecture_patterns",
            "reusable_components": f"{settings.qdrant.collection_prefix}_reusable_components",
        }
        self._initialize_collections()

    def _initialize_collections(self) -> None:
        """Initialize Qdrant collections if they don't exist."""
        for collection_name in self.collections.values():
            try:
                collections = self.client.get_collections().collections
                existing = [c.name for c in collections]

                if collection_name not in existing:
                    self.client.create_collection(
                        collection_name=collection_name,
                        vectors_config=models.VectorParams(
                            size=settings.qdrant.vector_size,
                            distance=models.Distance.COSINE,
                        ),
                    )
                    logger.info(f"Created collection: {collection_name}")
                else:
                    logger.info(f"Collection already exists: {collection_name}")
            except Exception as e:
                logger.error(f"Failed to initialize collection {collection_name}: {e}")
                raise

    def store_embedding(
        self,
        collection_type: str,
        text: str,
        vector: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Store an embedding with metadata."""
        if collection_type not in self.collections:
            raise ValueError(f"Unknown collection type: {collection_type}")

        collection_name = self.collections[collection_type]
        point_id = str(uuid.uuid4())

        self.client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "text": text,
                        "metadata": metadata or {},
                        "created_at": str(uuid.uuid1().time),
                    },
                )
            ],
        )

        logger.info(f"Stored embedding in {collection_type}: {point_id}")
        return point_id

    def search_similar(
        self,
        collection_type: str,
        query_vector: list[float],
        limit: int = 5,
        score_threshold: float = 0.7,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search for similar embeddings."""
        if collection_type not in self.collections:
            raise ValueError(f"Unknown collection type: {collection_type}")

        collection_name = self.collections[collection_type]

        # Build filter if metadata_filter provided
        query_filter = None
        if metadata_filter:
            conditions = []
            for key, value in metadata_filter.items():
                conditions.append(
                    models.FieldCondition(
                        key=f"metadata.{key}",
                        match=models.MatchValue(value=value),
                    )
                )
            if conditions:
                query_filter = models.Filter(must=conditions)

        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=limit,
            score_threshold=score_threshold,
        )

        return [
            {
                "id": result.id,
                "score": result.score,
                "text": result.payload.get("text") if result.payload else None,
                "metadata": result.payload.get("metadata") if result.payload else None,
            }
            for result in results
        ]

    def delete_collection(self, collection_type: str) -> None:
        """Delete a collection."""
        if collection_type not in self.collections:
            raise ValueError(f"Unknown collection type: {collection_type}")

        collection_name = self.collections[collection_type]
        self.client.delete_collection(collection_name=collection_name)
        logger.info(f"Deleted collection: {collection_name}")

    def get_collection_stats(self, collection_type: str) -> dict[str, Any]:
        """Get statistics for a collection."""
        if collection_type not in self.collections:
            raise ValueError(f"Unknown collection type: {collection_type}")

        collection_name = self.collections[collection_type]
        info = self.client.get_collection(collection_name=collection_name)

        return {
            "collection_name": collection_name,
            "points_count": info.points_count,
            "vectors_count": info.vectors_count,
            "indexed_vectors_count": info.indexed_vectors_count,
        }
