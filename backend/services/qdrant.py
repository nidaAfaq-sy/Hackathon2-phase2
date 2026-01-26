"""
Qdrant vector database service for task embeddings and semantic search
"""

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from typing import List, Optional, Dict, Any
from settings import settings
import logging

logger = logging.getLogger(__name__)


class QdrantService:
    """Service for managing vector operations with Qdrant"""

    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )
        self.collection_name = "tasks"

    def create_collection(self, vector_size: int = 384):
        """Create or recreate the tasks collection"""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name in collection_names:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return

            # Create collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=rest.VectorParams(
                    size=vector_size,
                    distance=rest.Distance.COSINE
                )
            )
            logger.info(f"Created collection '{self.collection_name}' with vector size {vector_size}")
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise

    def add_task_vector(self, task_id: str, user_id: str, vector: List[float], payload: Dict[str, Any]):
        """Add a task vector to Qdrant"""
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[rest.PointStruct(
                    id=task_id,
                    vector=vector,
                    payload={
                        **payload,
                        "user_id": user_id,
                        "task_id": task_id
                    }
                )]
            )
            logger.debug(f"Added vector for task {task_id}")
        except Exception as e:
            logger.error(f"Error adding task vector: {e}")
            raise

    def search_similar_tasks(self, user_id: str, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar tasks for a specific user"""
        try:
            hits = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=rest.Filter(
                    must=[
                        rest.FieldCondition(
                            key="user_id",
                            match=rest.MatchValue(value=user_id)
                        )
                    ]
                ),
                limit=limit,
                with_payload=True
            )

            results = []
            for hit in hits:
                results.append({
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                })

            return results
        except Exception as e:
            logger.error(f"Error searching similar tasks: {e}")
            raise

    def delete_task_vector(self, task_id: str):
        """Delete a task vector from Qdrant"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=rest.PointIdsList(points=[task_id])
            )
            logger.debug(f"Deleted vector for task {task_id}")
        except Exception as e:
            logger.error(f"Error deleting task vector: {e}")
            raise

    def update_task_vector(self, task_id: str, user_id: str, vector: List[float], payload: Dict[str, Any]):
        """Update an existing task vector"""
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[rest.PointStruct(
                    id=task_id,
                    vector=vector,
                    payload={
                        **payload,
                        "user_id": user_id,
                        "task_id": task_id
                    }
                )]
            )
            logger.debug(f"Updated vector for task {task_id}")
        except Exception as e:
            logger.error(f"Error updating task vector: {e}")
            raise

    def get_collection_info(self):
        """Get information about the collection"""
        try:
            info = self.client.get_collection(collection_name=self.collection_name)
            return {
                "name": info.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "config": {
                    "vector_size": info.config.params.vectors.size if info.config.params.vectors else None,
                    "distance": info.config.params.vectors.distance if info.config.params.vectors else None
                }
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            raise


# Global Qdrant service instance
qdrant_service = QdrantService()