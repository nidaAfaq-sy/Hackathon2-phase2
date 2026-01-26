# Backend CLAUDE.md

## 🎯 Backend Focus
FastAPI with JWT authentication and SQLModel database models

## ⚠️ CRITICAL RULES
1. **Specs control code. Code never leads specs.**
2. All implementation must reference spec files using `@specs/` syntax
3. JWT verification middleware required for all protected routes
4. User isolation must be enforced (user_id in JWT must match URL user_id)
5. Database models must use SQLModel with Neon PostgreSQL

## ✅ Implementation Checklist
- [ ] SQLModel models for users and tasks
- [ ] Neon PostgreSQL connection
- [ ] JWT verification middleware
- [ ] Authenticated task CRUD routes
- [ ] User isolation enforcement
- [ ] Proper error handling (401, 403)

## 📋 Referenced Specs
- @specs/features/task-crud.md
- @specs/features/authentication.md
- @specs/api/rest-endpoints.md
- @specs/database/schema.md

## 🛠 Tech Stack
- FastAPI
- SQLModel
- JWT
- Neon PostgreSQL
- Python