"""
Text embedding service using sentence transformers
"""

from sentence_transformers import SentenceTransformer
from typing import List
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        logger.info(f"Initialized embedding model: {model_name}")

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            if not text or not text.strip():
                return [0.0] * 384  # Default vector size for all-MiniLM-L6-v2

            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding for text: {e}")
            return [0.0] * 384

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            # Filter empty texts
            valid_texts = [text for text in texts if text and text.strip()]
            if not valid_texts:
                return [[0.0] * 384 for _ in texts]

            embeddings = self.model.encode(valid_texts, convert_to_numpy=True)
            embedding_list = embeddings.tolist()

            # Handle the case where some texts were filtered out
            result = []
            valid_index = 0
            for text in texts:
                if text and text.strip():
                    result.append(embedding_list[valid_index])
                    valid_index += 1
                else:
                    result.append([0.0] * 384)

            return result
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return [[0.0] * 384 for _ in texts]

    def get_vector_size(self) -> int:
        """Get the size of generated vectors"""
        return 384  # Size for all-MiniLM-L6-v2


# Global embedding service instance
embedding_service = EmbeddingService()