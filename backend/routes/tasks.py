from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select
from typing import List, Optional
from database import get_session
from models import (
    Task, TaskCreate, TaskRead, TaskUpdate, TaskFilter,
    ErrorResponse, TaskListResponse
)
from middleware.jwt import extract_user_id_from_token, validate_user_authorization, JWTPayload
from services.tasks import task_service
from fastapi import Header

router = APIRouter(
    prefix="/api/users/{user_id}/tasks",
    tags=["tasks"]
)


@router.get("/", response_model=TaskListResponse)
async def get_tasks(
    user_id: str,
    request: Request,
    completed: Optional[bool] = None,
    search: Optional[str] = None,
    authorization: str = Header(None),
    session: Session = Depends(get_session)
):
    """
    Get all tasks for a specific user with optional filtering.
    Security: JWT token required, user_id must match JWT user_id
    """
    # Get user from request state (set by JWT middleware)
    user_payload: JWTPayload = getattr(request.state, 'user', None)
    if not user_payload or user_payload.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own tasks",
        )

    # Use task service
    filter_obj = TaskFilter(completed=completed, search=search)
    tasks = task_service.get_tasks(session, user_id, filter_obj)

    return TaskListResponse(tasks=tasks)


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    request: Request,
    authorization: str = Header(None),
    session: Session = Depends(get_session)
):
    """
    Create a new task for a specific user.
    Security: JWT token required, user_id must match JWT user_id
    """
    # Get user from request state (set by JWT middleware)
    user_payload: JWTPayload = getattr(request.state, 'user', None)
    if not user_payload or user_payload.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own tasks",
        )

    # Use task service
    task = task_service.create_task(session, user_id, task_data)
    return task


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    user_id: str,
    task_id: str,
    request: Request,
    authorization: str = Header(None),
    session: Session = Depends(get_session)
):
    """
    Get a specific task by ID.
    Security: JWT token required, user_id must match JWT user_id
    """
    # Get user from request state (set by JWT middleware)
    user_payload: JWTPayload = getattr(request.state, 'user', None)
    if not user_payload or user_payload.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own tasks",
        )

    # Get task
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify task belongs to user (compare UUID with string)
    if str(task.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own tasks",
        )

    return task


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    user_id: str,
    task_id: str,
    task_data: TaskUpdate,
    request: Request,
    authorization: str = Header(None),
    session: Session = Depends(get_session)
):
    """
    Update an existing task.
    Security: JWT token required, user_id must match JWT user_id
    """
    # Get user from request state (set by JWT middleware)
    user_payload: JWTPayload = getattr(request.state, 'user', None)
    if not user_payload or user_payload.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own tasks",
        )

    # Use task service
    task = task_service.update_task(session, user_id, task_id, task_data)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: str,
    request: Request,
    authorization: str = Header(None),
    session: Session = Depends(get_session)
):
    """
    Delete a task.
    Security: JWT token required, user_id must match JWT user_id
    """
    # Get user from request state (set by JWT middleware)
    user_payload: JWTPayload = getattr(request.state, 'user', None)
    if not user_payload or user_payload.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own tasks",
        )

    # Use task service
    success = task_service.delete_task(session, user_id, task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )

    return None


@router.get("/{task_id}/similar", response_model=TaskListResponse)
async def get_similar_tasks(
    user_id: str,
    task_id: str,
    request: Request,
    limit: int = 5,
    authorization: str = Header(None),
    session: Session = Depends(get_session)
):
    """
    Get similar tasks using semantic search.
    Security: JWT token required, user_id must match JWT user_id
    """
    # Get user from request state (set by JWT middleware)
    user_payload: JWTPayload = getattr(request.state, 'user', None)
    if not user_payload or user_payload.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own tasks",
        )

    # Use task service for semantic search
    tasks = task_service.search_tasks_semantic(session, user_id, task_id, limit)

    return TaskListResponse(tasks=tasks)