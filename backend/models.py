from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel
import json


class UserBase(SQLModel):
    """Base user model for validation"""
    email: str = Field(
        unique=True,
        index=True,
        min_length=5,
        max_length=100
    )


class User(UserBase, table=True):
    """User model for authentication and task ownership"""
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    # Relationship to tasks
    tasks: List["Task"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    """Schema for creating new users"""
    pass


class UserRead(UserBase):
    """Schema for reading user data"""
    id: UUID
    created_at: datetime


class TaskBase(SQLModel):
    """Base task model for validation"""
    title: str = Field(
        min_length=1,
        max_length=200
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000
    )
    completed: bool = Field(
        default=False
    )


class Task(TaskBase, table=True):
    """Task model for todo items"""
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True
    )
    user_id: UUID = Field(
        foreign_key="user.id",
        nullable=False,
        index=True
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    # Vector embedding for semantic search
    embedding: Optional[str] = Field(
        default=None,
        sa_column_kwargs={"server_default": "[]"}
    )

    # Relationship to user
    user: Optional[User] = Relationship(back_populates="tasks")

    def set_embedding(self, embedding: List[float]):
        """Set the embedding vector as JSON string"""
        self.embedding = json.dumps(embedding)

    def get_embedding(self) -> List[float]:
        """Get the embedding vector from JSON string"""
        if self.embedding:
            return json.loads(self.embedding)
        return []


class TaskCreate(TaskBase):
    """Schema for creating new tasks"""
    pass


class TaskRead(TaskBase):
    """Schema for reading task data"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


class TaskUpdate(SQLModel):
    """Schema for updating tasks"""
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000
    )
    completed: Optional[bool] = Field(default=None)


class TaskFilter(BaseModel):
    """Schema for task filtering"""
    completed: Optional[bool] = None
    search: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response schema"""
    error: str
    message: str


class TaskListResponse(BaseModel):
    """Response schema for task list"""
    tasks: List[TaskRead]