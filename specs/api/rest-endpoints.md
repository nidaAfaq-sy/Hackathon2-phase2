# REST API Endpoints Specification

## 🌐 Base URL Structure
```
Frontend: http://localhost:3000
Backend:  http://localhost:8000
API Base: http://localhost:8000/api
```

## 🔐 Authentication Requirements
All endpoints except auth routes require:
- **Header**: `Authorization: Bearer <JWT>`
- **Validation**: JWT must be valid and not expired
- **User Match**: JWT user_id must match URL user_id parameter

## 📋 Endpoint Reference

### Authentication Endpoints (Better Auth)
```
GET  /api/auth/signin     → Login page
POST /api/auth/signin     → Submit login
GET  /api/auth/signup     → Registration page
POST /api/auth/signup     → Submit registration
GET  /api/auth/signout    → Logout page
POST /api/auth/signout    → Submit logout
GET  /api/auth/callback   → OAuth callback
GET  /api/auth/me         → Get current user (JWT protected)
```

### Task Management Endpoints

#### 1. Get User's Tasks
```
GET /api/users/{user_id}/tasks
```
- **Description**: Retrieve all tasks for authenticated user
- **Parameters**:
  - `user_id` (path): User ID from JWT (must match)
- **Response**: 200 OK
```json
{
  "tasks": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "title": "Task title",
      "description": "Task description",
      "completed": false,
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z"
    }
  ]
}
```

#### 2. Create New Task
```
POST /api/users/{user_id}/tasks
```
- **Description**: Create a new task for authenticated user
- **Parameters**:
  - `user_id` (path): User ID from JWT (must match)
- **Request Body**:
```json
{
  "title": "Task title",
  "description": "Task description (optional)",
  "completed": false
}
```
- **Response**: 201 Created
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "Task title",
  "description": "Task description",
  "completed": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

#### 3. Get Specific Task
```
GET /api/users/{user_id}/tasks/{task_id}
```
- **Description**: Get a specific task by ID
- **Parameters**:
  - `user_id` (path): User ID from JWT (must match)
  - `task_id` (path): Task ID
- **Response**: 200 OK
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "Task title",
  "description": "Task description",
  "completed": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

#### 4. Update Task
```
PUT /api/users/{user_id}/tasks/{task_id}
```
- **Description**: Update an existing task
- **Parameters**:
  - `user_id` (path): User ID from JWT (must match)
  - `task_id` (path): Task ID to update
- **Request Body**:
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "completed": true
}
```
- **Response**: 200 OK
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "Updated title",
  "description": "Updated description",
  "completed": true,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```

#### 5. Delete Task
```
DELETE /api/users/{user_id}/tasks/{task_id}
```
- **Description**: Delete a task
- **Parameters**:
  - `user_id` (path): User ID from JWT (must match)
  - `task_id` (path): Task ID to delete
- **Response**: 204 No Content

## ⚠️ Error Responses

### Authentication Errors
```json
// 401 Unauthorized
{
  "error": "Unauthorized",
  "message": "Authentication required"
}

// 403 Forbidden
{
  "error": "Forbidden",
  "message": "You can only access your own tasks"
}
```

### Validation Errors
```json
// 400 Bad Request
{
  "error": "Validation Error",
  "message": "Title is required and must be 1-200 characters"
}

// 422 Unprocessable Entity
{
  "error": "Invalid Data",
  "message": "Invalid field values"
}
```

### Resource Errors
```json
// 404 Not Found
{
  "error": "Not Found",
  "message": "Task not found"
}
```

## 🔧 Request/Response Examples

### Creating a Task
```bash
curl -X POST "http://localhost:8000/api/users/123/tasks" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "completed": false
  }'
```

### Getting User's Tasks
```bash
curl -X GET "http://localhost:8000/api/users/123/tasks" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Updating a Task
```bash
curl -X PUT "http://localhost:8000/api/users/123/tasks/456" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, bread, eggs, cheese",
    "completed": true
  }'
```

## 🛡️ Security Considerations

### JWT Validation
- All protected endpoints validate JWT signature
- Token expiration automatically checked
- User ID extracted and validated against URL

### Input Validation
- All input fields validated server-side
- SQL injection protection via SQLModel
- XSS protection via input sanitization

### Rate Limiting
- API endpoints protected from abuse
- Reasonable request limits per user
- Monitoring for suspicious activity