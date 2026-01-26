# Phase II Full-Stack Todo App - Architecture Specification

## 🏗️ System Architecture

### Component Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js UI    │    │   FastAPI API   │    │ Neon PostgreSQL │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Database)    │
│                 │    │                 │    │                 │
│ • Better Auth   │    │ • JWT Middleware│    │ • SQLModel      │
│ • Task UI       │    │ • Task Routes   │    │ • User Model    │
│ • API Client    │    │ • Auth Routes   │    │ • Task Model    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔐 Authentication Flow

### JWT-Based Authentication
1. **User Registration/Login**: Better Auth handles user credentials
2. **Token Issuance**: JWT token issued and stored in HTTP-only cookie
3. **Frontend API Calls**: Token automatically attached to requests
4. **Backend Verification**: JWT middleware validates token on protected routes
5. **User Authorization**: User ID in JWT must match URL user_id parameter

### Authentication Sequence
```
1. User submits login form → Better Auth
2. Better Auth validates credentials → Issues JWT
3. Frontend stores JWT in cookie
4. Frontend makes API call → JWT automatically attached
5. Backend JWT middleware → Verifies token
6. Route handler → Validates user_id match
7. Database query → Filters by user_id
```

## 🗄️ Database Architecture

### SQLModel Models
- **User Model**: Basic user information, Better Auth integration
- **Task Model**: Task details with foreign key to User
- **Relationships**: One-to-many (User → Tasks)

### Database Schema
```sql
Users table:
- id: UUID (primary key)
- email: VARCHAR (unique, indexed)
- created_at: TIMESTAMP

Tasks table:
- id: UUID (primary key)
- user_id: UUID (foreign key to users.id)
- title: VARCHAR
- description: TEXT
- completed: BOOLEAN
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

## 🌐 API Architecture

### REST Endpoints
- **Auth**: `/api/auth/*` (Better Auth handled)
- **Tasks**: `/api/users/{user_id}/tasks/*` (JWT protected)
- **CRUD Operations**: Standard HTTP methods (GET, POST, PUT, DELETE)

### Request/Response Patterns
- **Headers**: Authorization: Bearer <JWT>
- **Responses**: JSON with standardized error handling
- **Status Codes**: 200 (OK), 201 (Created), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found)

## 🎨 Frontend Architecture

### Next.js Structure
```
/src
├── app/
│   ├── layout.tsx (Global layout)
│   ├── page.tsx (Home/Dashboard)
│   ├── tasks/ (Task management pages)
│   └── auth/ (Login/Register pages)
├── components/
│   ├── TaskList.tsx
│   ├── TaskForm.tsx
│   └── AuthForm.tsx
├── lib/
│   ├── api.ts (API client)
│   └── auth.ts (Auth utilities)
└── styles/
    └── globals.css
```

### Better Auth Integration
- **Provider**: Wraps entire application
- **Session Management**: Automatic token handling
- **Protected Routes**: Middleware for authentication checks
- **JWT Plugin**: Enables JWT token exchange

## 🔧 Development Environment

### Docker Services
- **frontend**: Next.js development server
- **backend**: FastAPI development server
- **postgres**: Neon PostgreSQL database
- **Network**: Internal communication between services

### Environment Variables
- **BETTER_AUTH_SECRET**: JWT signing secret
- **DATABASE_URL**: Neon PostgreSQL connection string
- **FRONTEND_URL**: Frontend origin for CORS
- **BACKEND_URL**: Backend API base URL

## 🛡️ Security Architecture

### Multi-Layer Security
1. **Transport**: HTTPS/TLS encryption
2. **Authentication**: JWT with expiration
3. **Authorization**: User ID validation
4. **Database**: User isolation at query level
5. **Input Validation**: Schema validation on all endpoints

### Security Headers & CORS
- **CORS**: Restricted to frontend origin
- **Headers**: Security headers for production
- **Rate Limiting**: API throttling (future enhancement)