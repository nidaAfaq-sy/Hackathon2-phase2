"""
Authorization tests to verify user isolation
"""

import pytest
from fastapi.testclient import TestClient
from main import app
import jwt
from settings import settings
from database import get_session, engine
from sqlmodel import Session, SQLModel, select
from models import User, Task


client = TestClient(app)


def create_test_jwt(user_id: str, email: str = "test@example.com"):
    """Create a test JWT token"""
    payload = {
        "user_id": user_id,
        "email": email,
        "iat": 1234567890,
        "exp": 1234571490  # 1 hour later
    }
    return jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_test_user(user_id: str, email: str):
    """Create a test user in the database"""
    with Session(engine) as session:
        user = User(id=user_id, email=email)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def create_test_task(user_id: str, title: str):
    """Create a test task in the database"""
    with Session(engine) as session:
        task = Task(user_id=user_id, title=title)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task


def test_user_can_only_see_own_tasks():
    """Test that users can only see tasks that belong to them"""

    # Create test users
    user1 = create_test_user("user-123", "user1@example.com")
    user2 = create_test_user("user-456", "user2@example.com")

    # Create tasks for each user
    task1 = create_test_task(user1.id, "User 1 Task")
    task2 = create_test_task(user1.id, "User 1 Another Task")
    task3 = create_test_task(user2.id, "User 2 Task")

    user1_token = create_test_jwt(user1.id)
    user2_token = create_test_jwt(user2.id)

    try:
        # User 1 should only see their own tasks
        response = client.get(
            f"/users/{user1.id}/tasks",
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        assert response.status_code == 200
        tasks = response.json()["tasks"]
        assert len(tasks) == 2
        task_ids = [task["id"] for task in tasks]
        assert task1.id in task_ids
        assert task2.id in task_ids
        assert task3.id not in task_ids

        # User 2 should only see their own tasks
        response = client.get(
            f"/users/{user2.id}/tasks",
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        assert response.status_code == 200
        tasks = response.json()["tasks"]
        assert len(tasks) == 1
        assert tasks[0]["id"] == str(task3.id)

    finally:
        # Cleanup
        with Session(engine) as session:
            session.delete(task1)
            session.delete(task2)
            session.delete(task3)
            session.delete(user1)
            session.delete(user2)
            session.commit()


def test_user_cannot_access_other_users_tasks_by_id():
    """Test that users cannot access specific tasks by ID if they don't own them"""

    # Create test users
    user1 = create_test_user("user-123", "user1@example.com")
    user2 = create_test_user("user-456", "user2@example.com")

    # Create tasks
    task1 = create_test_task(user1.id, "User 1 Task")
    task2 = create_test_task(user2.id, "User 2 Task")

    user1_token = create_test_jwt(user1.id)

    try:
        # User 1 should be able to access their own task
        response = client.get(
            f"/users/{user1.id}/tasks/{task1.id}",
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        assert response.status_code == 200
        assert response.json()["id"] == str(task1.id)

        # User 1 should NOT be able to access User 2's task
        response = client.get(
            f"/users/{user1.id}/tasks/{task2.id}",
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        assert response.status_code == 403
        assert "You can only access your own tasks" in response.json()["detail"]

    finally:
        # Cleanup
        with Session(engine) as session:
            session.delete(task1)
            session.delete(task2)
            session.delete(user1)
            session.delete(user2)
            session.commit()


def test_user_cannot_modify_other_users_tasks():
    """Test that users cannot modify tasks they don't own"""

    # Create test users
    user1 = create_test_user("user-123", "user1@example.com")
    user2 = create_test_user("user-456", "user2@example.com")

    # Create tasks
    task1 = create_test_task(user1.id, "User 1 Task")
    task2 = create_test_task(user2.id, "User 2 Task")

    user1_token = create_test_jwt(user1.id)

    try:
        # User 1 should NOT be able to update User 2's task
        response = client.put(
            f"/users/{user1.id}/tasks/{task2.id}",
            headers={"Authorization": f"Bearer {user1_token}"},
            json={"title": "Hacked Task"}
        )
        assert response.status_code == 403
        assert "You can only access your own tasks" in response.json()["detail"]

        # User 1 should NOT be able to delete User 2's task
        response = client.delete(
            f"/users/{user1.id}/tasks/{task2.id}",
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        assert response.status_code == 403
        assert "You can only access your own tasks" in response.json()["detail"]

        # Verify the task wasn't modified
        with Session(engine) as session:
            updated_task = session.get(Task, task2.id)
            assert updated_task.title == "User 2 Task"  # Original title

    finally:
        # Cleanup
        with Session(engine) as session:
            session.delete(task1)
            session.delete(task2)
            session.delete(user1)
            session.delete(user2)
            session.commit()


def test_database_level_user_isolation():
    """Test that database queries are properly filtered by user_id"""

    # Create test users
    user1 = create_test_user("user-123", "user1@example.com")
    user2 = create_test_user("user-456", "user2@example.com")

    # Create tasks
    task1 = create_test_task(user1.id, "User 1 Task")
    task2 = create_test_task(user1.id, "User 1 Another Task")
    task3 = create_test_task(user2.id, "User 2 Task")

    user1_token = create_test_jwt(user1.id)

    try:
        # Get all tasks for User 1
        response = client.get(
            f"/users/{user1.id}/tasks",
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        assert response.status_code == 200
        tasks = response.json()["tasks"]

        # Verify only User 1's tasks are returned
        assert len(tasks) == 2
        for task in tasks:
            assert task["user_id"] == str(user1.id)

        # Verify User 2's task is not in the results
        task_ids = [task["id"] for task in tasks]
        assert str(task3.id) not in task_ids

    finally:
        # Cleanup
        with Session(engine) as session:
            session.delete(task1)
            session.delete(task2)
            session.delete(task3)
            session.delete(user1)
            session.delete(user2)
            session.commit()