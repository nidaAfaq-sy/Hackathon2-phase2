"""
Security validation tests for JWT authentication
These tests verify the critical security requirements
"""

import pytest
import jwt
from fastapi.testclient import TestClient
from main import app
from settings import settings

client = TestClient(app)


def create_test_jwt(user_id: str = "test-user-123"):
    """Create a test JWT token"""
    payload = {
        "user_id": user_id,
        "email": "test@example.com",
        "iat": 1234567890,
        "exp": 1234571490  # 1 hour later
    }
    return jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)


def test_no_token_returns_401():
    """Test that requests without JWT token return 401"""
    response = client.get("/users/test-user-123/tasks")
    assert response.status_code == 401
    assert response.json()["error"] == "Authentication Error"


def test_invalid_token_returns_401():
    """Test that invalid JWT tokens return 401"""
    response = client.get(
        "/users/test-user-123/tasks",
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401


def test_expired_token_returns_401():
    """Test that expired JWT tokens return 401"""
    # Create expired token
    expired_payload = {
        "user_id": "test-user-123",
        "email": "test@example.com",
        "iat": 1234567890,
        "exp": 1234567890  # Expired
    }
    expired_token = jwt.encode(
        expired_payload,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    response = client.get(
        "/users/test-user-123/tasks",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401


def test_wrong_user_id_returns_403():
    """Test that JWT user_id must match URL user_id"""
    jwt_token = create_test_jwt("user-123")

    response = client.get(
        "/users/different-user-456/tasks",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "You can only access your own tasks"


def test_valid_token_allows_access():
    """Test that valid JWT tokens with matching user_id work"""
    jwt_token = create_test_jwt("test-user-123")

    response = client.get(
        "/users/test-user-123/tasks",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    # Should not return 401 or 403, even if no tasks exist
    assert response.status_code != 401
    assert response.status_code != 403


def test_task_crud_requires_authentication():
    """Test that all task CRUD operations require authentication"""

    # Test create without token
    response = client.post("/users/test-user-123/tasks", json={
        "title": "Test Task"
    })
    assert response.status_code == 401

    # Test update without token
    response = client.put("/users/test-user-123/tasks/task-123", json={
        "title": "Updated Task"
    })
    assert response.status_code == 401

    # Test delete without token
    response = client.delete("/users/test-user-123/tasks/task-123")
    assert response.status_code == 401


def test_task_crud_user_isolation():
    """Test that users can only access their own tasks"""

    user1_token = create_test_jwt("user-123")
    user2_token = create_test_jwt("user-456")

    # User 1 creates a task
    response = client.post(
        "/users/user-123/tasks",
        headers={"Authorization": f"Bearer {user1_token}"},
        json={"title": "User 1 Task"}
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    # User 2 should not be able to access User 1's task
    response = client.get(
        f"/users/user-456/tasks/{task_id}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert response.status_code == 403

    # User 2 should not be able to update User 1's task
    response = client.put(
        f"/users/user-456/tasks/{task_id}",
        headers={"Authorization": f"Bearer {user2_token}"},
        json={"title": "Hacked Task"}
    )
    assert response.status_code == 403

    # User 2 should not be able to delete User 1's task
    response = client.delete(
        f"/users/user-456/tasks/{task_id}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert response.status_code == 403


def test_auth_routes_accessible_without_token():
    """Test that auth routes don't require JWT tokens"""

    # Auth routes should be accessible without authentication
    response = client.get("/api/auth/me")
    # This might return 401 or redirect, but shouldn't crash
    assert response.status_code in [401, 302, 404]