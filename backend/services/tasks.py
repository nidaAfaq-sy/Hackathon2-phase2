"""
Task service with vector embeddings and semantic search
"""

from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from models import Task, TaskCreate, TaskUpdate, TaskFilter
from services.embeddings import embedding_service
from services.qdrant import qdrant_service
import logging

logger = logging.getLogger(__name__)


class TaskService:
    """Service for task operations with semantic search capabilities"""

    def __init__(self):
        # Collection will be created lazily when first needed
        self._collection_initialized = False

    def _ensure_collection(self):
        """Ensure Qdrant collection exists (lazy initialization)"""
        if not self._collection_initialized:
            try:
                qdrant_service.create_collection()
                self._collection_initialized = True
            except Exception as e:
                logger.warning(f"Failed to initialize Qdrant collection: {e}. Semantic search may not be available.")

    def _generate_task_embedding(self, task: Task) -> List[float]:
        """Generate embedding for a task based on title and description"""
        text = f"{task.title} {task.description or ''}"
        return embedding_service.generate_embedding(text)

    def _get_search_text(self, task_data: TaskCreate) -> str:
        """Get search text for embedding generation"""
        return f"{task_data.title} {task_data.description or ''}"

    def create_task(self, session: Session, user_id: UUID, task_data: TaskCreate) -> Task:
        """Create a new task with vector embedding"""
        try:
            # Ensure Qdrant collection exists
            self._ensure_collection()
            
            # Convert to UUID if string
            user_id_uuid = user_id if isinstance(user_id, UUID) else UUID(user_id)
            
            # Create task in database
            task = Task(
                user_id=user_id_uuid,
                title=task_data.title,
                description=task_data.description,
                completed=task_data.completed or False
            )

            session.add(task)
            session.commit()
            session.refresh(task)

            # Generate and store embedding
            embedding = self._generate_task_embedding(task)
            task.set_embedding(embedding)
            session.add(task)
            session.commit()

            # Add to Qdrant (optional - don't fail if Qdrant is unavailable)
            try:
                qdrant_service.add_task_vector(
                    task_id=str(task.id),
                    user_id=str(user_id_uuid),
                    vector=embedding,
                    payload={
                        "title": task.title,
                        "description": task.description,
                        "completed": task.completed,
                        "created_at": task.created_at.isoformat()
                    }
                )
                logger.info(f"Created task {task.id} with embedding and Qdrant vector")
            except Exception as qdrant_error:
                logger.warning(f"Failed to add task vector to Qdrant (task still created): {qdrant_error}")

            logger.info(f"Created task {task.id} with embedding")
            return task

        except Exception as e:
            session.rollback()
            logger.error(f"Error creating task: {e}")
            raise

    def get_tasks(self, session: Session, user_id: UUID, filter: Optional[TaskFilter] = None) -> List[Task]:
        """Get tasks for a user with optional filtering"""
        try:
            # Convert to UUID if string
            user_id_uuid = user_id if isinstance(user_id, UUID) else UUID(user_id)
            query = select(Task).where(Task.user_id == user_id_uuid)

            if filter:
                if filter.completed is not None:
                    query = query.where(Task.completed == filter.completed)
                if filter.search:
                    search_text = filter.search.lower()
                    query = query.where(
                        (Task.title.contains(search_text)) |
                        (Task.description.contains(search_text) if Task.description else False)
                    )

            tasks = session.exec(query).all()
            return list(tasks)

        except Exception as e:
            logger.error(f"Error getting tasks: {e}")
            raise

    def get_task(self, session: Session, user_id: UUID, task_id: UUID) -> Optional[Task]:
        """Get a specific task"""
        try:
            # Convert to UUID if strings
            task_id_uuid = task_id if isinstance(task_id, UUID) else UUID(task_id)
            user_id_uuid = user_id if isinstance(user_id, UUID) else UUID(user_id)
            
            task = session.get(Task, task_id_uuid)
            if task and task.user_id == user_id_uuid:
                return task
            return None
        except Exception as e:
            logger.error(f"Error getting task: {e}")
            raise

    def update_task(self, session: Session, user_id: UUID, task_id: UUID, task_data: TaskUpdate) -> Optional[Task]:
        """Update a task and its embedding"""
        try:
            # Ensure Qdrant collection exists
            self._ensure_collection()
            
            # Convert to UUID if strings
            task_id_uuid = task_id if isinstance(task_id, UUID) else UUID(task_id)
            user_id_uuid = user_id if isinstance(user_id, UUID) else UUID(user_id)
            
            task = session.get(Task, task_id_uuid)
            if not task or task.user_id != user_id_uuid:
                return None

            # Update task fields
            for field, value in task_data.dict(exclude_unset=True).items():
                setattr(task, field, value)

            # Update embedding if title or description changed
            update_embedding = False
            if task_data.title is not None or task_data.description is not None:
                embedding = self._generate_task_embedding(task)
                task.set_embedding(embedding)
                update_embedding = True

            session.add(task)
            session.commit()
            session.refresh(task)

            # Update Qdrant if embedding changed (optional - don't fail if Qdrant is unavailable)
            if update_embedding:
                try:
                    qdrant_service.update_task_vector(
                        task_id=str(task_id_uuid),
                        user_id=str(user_id_uuid),
                        vector=task.get_embedding(),
                        payload={
                            "title": task.title,
                            "description": task.description,
                            "completed": task.completed,
                            "updated_at": task.updated_at.isoformat()
                        }
                    )
                    logger.info(f"Updated task {task_id_uuid} vector in Qdrant")
                except Exception as qdrant_error:
                    logger.warning(f"Failed to update task vector in Qdrant (task still updated): {qdrant_error}")

            logger.info(f"Updated task {task_id_uuid}")
            return task

        except Exception as e:
            session.rollback()
            logger.error(f"Error updating task: {e}")
            raise

    def delete_task(self, session: Session, user_id: UUID, task_id: UUID) -> bool:
        """Delete a task and its vector"""
        try:
            # Ensure Qdrant collection exists
            self._ensure_collection()
            
            # Convert to UUID if strings
            task_id_uuid = task_id if isinstance(task_id, UUID) else UUID(task_id)
            user_id_uuid = user_id if isinstance(user_id, UUID) else UUID(user_id)
            
            task = session.get(Task, task_id_uuid)
            if not task or task.user_id != user_id_uuid:
                return False

            # Delete from Qdrant
            qdrant_service.delete_task_vector(str(task_id_uuid))

            # Delete from database
            session.delete(task)
            session.commit()

            logger.info(f"Deleted task {task_id}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting task: {e}")
            raise

    def search_tasks_semantic(self, user_id: UUID, query: str, limit: int = 5) -> List[Task]:
        """Search tasks using semantic similarity"""
        try:
            # Ensure Qdrant collection exists
            self._ensure_collection()
            
            # Generate query embedding
            query_vector = embedding_service.generate_embedding(query)

            # Search in Qdrant
            results = qdrant_service.search_similar_tasks(
                user_id=str(user_id),
                query_vector=query_vector,
                limit=limit
            )

            # Convert to Task objects (simplified for now)
            # In a real implementation, you'd fetch the actual Task objects from the database
            tasks = []
            for result in results:
                # This is a simplified representation
                # In practice, you'd query the database for these task IDs
                tasks.append({
                    "id": result["id"],
                    "score": result["score"],
                    "payload": result["payload"]
                })

            return tasks

        except Exception as e:
            logger.error(f"Error searching tasks semantically: {e}")
            raise

    def get_collection_info(self):
        """Get Qdrant collection information"""
        try:
            return qdrant_service.get_collection_info()
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            raise


# Global task service instance
task_service = TaskService()