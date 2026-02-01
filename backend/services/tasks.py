"""
Task service for CRUD operations
"""

from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from models import Task, TaskCreate, TaskUpdate, TaskFilter
import logging

logger = logging.getLogger(__name__)


class TaskService:
    """Service for task operations"""

    def create_task(self, session: Session, user_id: UUID, task_data: TaskCreate) -> Task:
        """Create a new task"""
        try:
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

            logger.info(f"Created task {task.id}")
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
        """Update a task"""
        try:
            # Convert to UUID if strings
            task_id_uuid = task_id if isinstance(task_id, UUID) else UUID(task_id)
            user_id_uuid = user_id if isinstance(user_id, UUID) else UUID(user_id)

            task = session.get(Task, task_id_uuid)
            if not task or task.user_id != user_id_uuid:
                return None

            # Update task fields
            for field, value in task_data.dict(exclude_unset=True).items():
                setattr(task, field, value)

            session.add(task)
            session.commit()
            session.refresh(task)

            logger.info(f"Updated task {task_id_uuid}")
            return task

        except Exception as e:
            session.rollback()
            logger.error(f"Error updating task: {e}")
            raise

    def delete_task(self, session: Session, user_id: UUID, task_id: UUID) -> bool:
        """Delete a task"""
        try:
            # Convert to UUID if strings
            task_id_uuid = task_id if isinstance(task_id, UUID) else UUID(task_id)
            user_id_uuid = user_id if isinstance(user_id, UUID) else UUID(user_id)

            task = session.get(Task, task_id_uuid)
            if not task or task.user_id != user_id_uuid:
                return False

            # Delete from database
            session.delete(task)
            session.commit()

            logger.info(f"Deleted task {task_id}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting task: {e}")
            raise


# Global task service instance
task_service = TaskService()
