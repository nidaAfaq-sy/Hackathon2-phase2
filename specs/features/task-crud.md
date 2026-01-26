# Task CRUD Feature Specification

## 📋 User Stories

### As a User, I can create tasks
- **Given** I am logged in and viewing the task list
- **When** I click "Add Task" and fill in the form
- **Then** A new task is created and appears in my task list

### As a User, I can view my tasks
- **Given** I am logged in
- **When** I visit the task list page
- **Then** I see only my tasks displayed in a list

### As a User, I can update my tasks
- **Given** I have existing tasks
- **When** I edit a task and save changes
- **Then** The task is updated with my changes

### As a User, I can mark tasks complete
- **Given** I have pending tasks
- **When** I toggle the complete status
- **Then** The task status is updated accordingly

### As a User, I can delete my tasks
- **Given** I have existing tasks
- **When** I click delete on a task
- **Then** The task is removed from my list

## ✅ Acceptance Criteria

### Task Creation
- **Fields**: Title (required), Description (optional), Completed (default: false)
- **Validation**: Title must be 1-200 characters
- **Response**: 201 Created with task data
- **Error**: 400 Bad Request for invalid data

### Task Retrieval
- **Scope**: Only tasks belonging to authenticated user
- **Response**: 200 OK with array of tasks
- **Error**: 401 Unauthorized without token

### Task Update
- **Fields**: Can update title, description, completed status
- **Validation**: Same as creation
- **Response**: 200 OK with updated task data
- **Error**: 403 Forbidden for wrong user_id

### Task Deletion
- **Response**: 204 No Content on success
- **Error**: 404 Not Found for non-existent task
- **Error**: 403 Forbidden for wrong user_id

## 🔒 Authentication Requirements

### JWT Token Required
- All task operations require valid JWT token
- Token must be included in Authorization header
- Token expiration handled gracefully

### User Authorization
- User ID in JWT must match user ID in URL path
- Example: JWT contains user_id=123, URL must be `/users/123/tasks`
- 403 Forbidden returned for user mismatch

### Error Responses
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

// 400 Bad Request
{
  "error": "Validation Error",
  "message": "Title is required and must be 1-200 characters"
}
```

## 📊 Data Model

### Task Entity
```typescript
interface Task {
  id: string;              // UUID
  user_id: string;         // UUID (foreign key)
  title: string;           // 1-200 characters
  description?: string;    // Optional text
  completed: boolean;      // Default: false
  created_at: Date;        // Timestamp
  updated_at: Date;        // Timestamp
}
```

### Validation Rules
- **Title**: Required, 1-200 characters, trimmed
- **Description**: Optional, max 1000 characters
- **Completed**: Boolean, default false
- **User ID**: Must match authenticated user