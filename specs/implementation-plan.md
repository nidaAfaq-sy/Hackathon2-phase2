# Phase II Implementation Plan

## 🎯 Project Overview
Next.js + FastAPI Todo Application with JWT Authentication and Neon PostgreSQL

## 📋 Implementation Steps

### STEP 0 — Repo & Tooling Setup (One Time)
✅ **COMPLETED**: Monorepo structure created
✅ **COMPLETED**: CLAUDE.md files created
✅ **COMPLETED**: Spec files written

### STEP 1 — Write Phase II Specs ✅ **COMPLETED**
- ✅ @specs/overview.md - Project overview and objectives
- ✅ @specs/architecture.md - System architecture and components
- ✅ @specs/features/task-crud.md - Task CRUD user stories and acceptance criteria
- ✅ @specs/features/authentication.md - Better Auth and JWT flow
- ✅ @specs/api/rest-endpoints.md - API endpoints and request/response schemas
- ✅ @specs/database/schema.md - SQLModel models and database schema
- ✅ @specs/ui/components.md - UI component specifications
- ✅ @specs/ui/pages.md - Page structure and layouts

### STEP 2 — Generate Phase II Plan ✅ **COMPLETED**
This plan outlines the implementation approach.

### STEP 3 — Backend Implementation (FastAPI)

#### 3.1 Database Setup
**Files to Create:**
- `backend/models.py` - SQLModel User and Task models
- `backend/database.py` - Database connection and session management
- `backend/settings.py` - Configuration and environment variables

**Implementation:**
- Implement SQLModel models from @specs/database/schema.md
- Setup Neon PostgreSQL connection
- Create database initialization script

#### 3.2 JWT Middleware
**Files to Create:**
- `backend/middleware/jwt.py` - JWT verification middleware
- `backend/auth.py` - Authentication utilities

**Implementation:**
- Create JWT verification middleware from @specs/features/authentication.md
- Extract user_id from JWT tokens
- Return 401 for invalid/missing tokens

#### 3.3 Task API Routes
**Files to Create:**
- `backend/routes/tasks.py` - Task CRUD endpoints
- `backend/routes/auth.py` - Authentication endpoints
- `backend/main.py` - FastAPI application setup

**Implementation:**
- Implement all endpoints from @specs/api/rest-endpoints.md
- Add user_id validation for all protected routes
- Ensure 403 for wrong user_id matches

#### 3.4 Error Handling
**Files to Update:**
- `backend/main.py` - Global error handlers

**Implementation:**
- Standardized error responses
- Proper HTTP status codes (401, 403, 400, 404)
- Validation error handling

### STEP 4 — Frontend Implementation (Next.js)

#### 4.1 Better Auth Setup
**Files to Create:**
- `frontend/src/app/layout.tsx` - Root layout with Better Auth provider
- `frontend/src/lib/auth.ts` - Auth configuration and utilities
- `frontend/src/components/AuthProvider.tsx` - Auth provider wrapper

**Implementation:**
- Configure Better Auth with JWT plugin from @specs/features/authentication.md
- Setup session management
- Configure JWT token handling

#### 4.2 API Client
**Files to Create:**
- `frontend/src/lib/api.ts` - API client with JWT attachment
- `frontend/src/lib/types.ts` - TypeScript interfaces

**Implementation:**
- Create API client from @specs/api/rest-endpoints.md
- Automatic JWT token attachment to requests
- Error handling and retry logic

#### 4.3 Task UI Components
**Files to Create:**
- `frontend/src/components/TaskList.tsx` - Task list component
- `frontend/src/components/TaskForm.tsx` - Task form component
- `frontend/src/components/TaskItem.tsx` - Individual task item
- `frontend/src/components/AuthForm.tsx` - Authentication forms

**Implementation:**
- Build components from @specs/ui/components.md
- Responsive design with Tailwind CSS
- Proper state management

#### 4.4 Task Pages
**Files to Create:**
- `frontend/src/app/page.tsx` - Dashboard page
- `frontend/src/app/tasks/page.tsx` - Task list page
- `frontend/src/app/tasks/new/page.tsx` - Create task page
- `frontend/src/app/tasks/[id]/page.tsx` - Edit task page
- `frontend/src/app/auth/signin/page.tsx` - Login page
- `frontend/src/app/auth/signup/page.tsx` - Registration page

**Implementation:**
- Build pages from @specs/ui/pages.md
- Navigation and routing
- Error boundaries and loading states

### STEP 5 — Security Validation (CRITICAL)

#### 5.1 Test Implementation
**Files to Create:**
- `backend/tests/test_authentication.py` - JWT auth tests
- `backend/tests/test_authorization.py` - User isolation tests
- `backend/tests/test_task_crud.py` - Task operations tests

**Test Scenarios:**
- ✅ No token → 401 Unauthorized
- ✅ Wrong user_id → 403 Forbidden
- ✅ Valid user → Only own tasks returned
- ✅ Expired JWT → 401 Unauthorized
- ✅ Invalid token → 401 Unauthorized

#### 5.2 Security Verification
**Implementation:**
- Manual testing of all security scenarios
- Automated test suite execution
- Security audit of code implementation

### STEP 6 — Docker & Env Setup

#### 6.1 Docker Configuration
**Files to Create:**
- `docker-compose.yml` - Multi-service configuration
- `frontend/Dockerfile` - Next.js container
- `backend/Dockerfile` - FastAPI container

**Services:**
- Frontend: Next.js development server
- Backend: FastAPI development server
- Database: Neon PostgreSQL (external) or local PostgreSQL for development

#### 6.2 Environment Configuration
**Files to Create:**
- `.env.example` - Environment variable template
- `README.md` - Setup and deployment instructions

**Environment Variables:**
- `BETTER_AUTH_SECRET` - JWT signing secret
- `DATABASE_URL` - Neon PostgreSQL connection
- `FRONTEND_URL` - Frontend origin
- `BACKEND_URL` - Backend API base URL

### STEP 7 — Final Review (Judging Criteria)

#### 7.1 Specification Compliance
**Verification:**
- ✅ All specs implemented as written
- ✅ No code without spec reference
- ✅ Proper @specs/ syntax usage

#### 7.2 Security Requirements
**Verification:**
- ✅ JWT authentication working
- ✅ User isolation enforced
- ✅ Proper error responses
- ✅ Database-level security

#### 7.3 Functionality Testing
**Verification:**
- ✅ All CRUD operations working
- ✅ Authentication flow complete
- ✅ Responsive UI working
- ✅ Error handling proper

## 🛠️ Implementation Guidelines

### Code Organization
- Follow spec-first approach strictly
- Reference specs using @specs/ syntax
- Maintain clear separation of concerns
- Use TypeScript for type safety

### Security Best Practices
- Validate all inputs server-side
- Never trust client-side validation
- Use HTTPS in production
- Implement proper CORS policies

### Performance Considerations
- Database query optimization
- Frontend state management
- API response caching (future)
- Bundle optimization

### Testing Strategy
- Unit tests for all components
- Integration tests for API endpoints
- Security tests for authentication
- End-to-end tests for critical flows

## 🚨 Critical Success Factors

1. **Spec Compliance**: All code must reference specs
2. **Security**: JWT auth and user isolation working
3. **Functionality**: Complete CRUD operations
4. **User Experience**: Responsive, accessible interface
5. **Code Quality**: Clean, maintainable codebase

## 📅 Estimated Timeline

- **Backend Setup**: 2-3 hours
- **Frontend Setup**: 3-4 hours
- **Security Validation**: 1-2 hours
- **Docker Setup**: 1 hour
- **Testing & Polish**: 2-3 hours

**Total Estimated Time**: 9-13 hours

## 🎯 Success Metrics

- ✅ All specs implemented without deviation
- ✅ Security tests passing (401/403 validation)
- ✅ Complete task CRUD functionality
- ✅ Responsive, accessible UI
- ✅ Proper error handling
- ✅ Docker containerization working