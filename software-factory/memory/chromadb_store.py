"""ChromaDB vector store adapter - lightweight alternative to Qdrant."""

import uuid
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from config.settings import settings
from observability.logger import get_logger

logger = get_logger(__name__)


class ChromaDBStore:
    """ChromaDB-based vector store for semantic memory (no Docker required)."""

    def __init__(self) -> None:
        # Initialize ChromaDB client
        db_path = getattr(settings, 'chroma_db_path', './chroma_db')
        
        self.client = chromadb.PersistentClient(path=db_path)
        
        self.collections = {
            "code_summaries": "code_summaries",
            "debug_fixes": "debug_fixes",
            "architecture_patterns": "architecture_patterns",
            "reusable_components": "reusable_components",
        }
        self._initialize_collections()

    def _initialize_collections(self) -> None:
        """Initialize ChromaDB collections if they don't exist."""
        for collection_name in self.collections.values():
            try:
                # Get or create collection
                self.client.get_or_create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}  # Use cosine similarity
                )
                logger.info(f"Initialized ChromaDB collection: {collection_name}")
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
        
        collection = self.client.get_collection(collection_name)

        # Add document with embedding
        collection.add(
            ids=[point_id],
            embeddings=[vector],
            documents=[text],
            metadatas=[metadata or {}],
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
        collection = self.client.get_collection(collection_name)

        # Query collection
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=limit,
            where=metadata_filter,  # ChromaDB uses 'where' for filtering
        )

        # Format results to match Qdrant interface
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                score = 1.0 - (results['distances'][0][i] if results['distances'] else 0.0)
                
                # Apply score threshold
                if score >= score_threshold:
                    formatted_results.append({
                        "id": doc_id,
                        "score": score,
                        "text": results['documents'][0][i] if results['documents'] else None,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else None,
                    })

        return formatted_results

    def delete_collection(self, collection_type: str) -> None:
        """Delete a collection."""
        if collection_type not in self.collections:
            raise ValueError(f"Unknown collection type: {collection_type}")

        collection_name = self.collections[collection_type]
        self.client.delete_collection(name=collection_name)
        logger.info(f"Deleted collection: {collection_name}")

    def get_collection_stats(self, collection_type: str) -> dict[str, Any]:
        """Get statistics for a collection."""
        if collection_type not in self.collections:
            raise ValueError(f"Unknown collection type: {collection_type}")

        collection_name = self.collections[collection_type]
        collection = self.client.get_collection(collection_name)
        
        count = collection.count()

        return {
            "collection_name": collection_name,
            "points_count": count,
            "vectors_count": count,
            "indexed_vectors_count": count,
        }
