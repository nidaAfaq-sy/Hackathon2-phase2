# Phase II Full-Stack Todo App - Root CLAUDE.md

## 🎯 Project Overview
Next.js + FastAPI Todo Application with JWT Authentication and Neon PostgreSQL

## ⚠️ CRITICAL RULES
1. **Specs control code. Code never leads specs.**
2. All implementation must reference spec files using `@specs/` syntax
3. Security requirements must be validated before deployment
4. JWT authentication must be implemented for all protected routes
5. User isolation must be enforced at database level

## 📋 Implementation Workflow
```
STEP 0 — Repo & Tooling Setup (One Time)
STEP 1 — Write Phase II Specs (MOST IMPORTANT)
STEP 2 — Generate Phase II Plan (MANDATORY)
STEP 3 — Backend Implementation (FastAPI)
STEP 4 — Frontend Implementation (Next.js)
STEP 5 — Security Validation (CRITICAL)
STEP 6 — Docker & Env Setup
STEP 7 — Final Review (Judging Criteria)
```

## 🚨 Security Requirements
- 401 without token
- 403 for wrong user_id
- Tasks filtered by user
- Expired JWT returns 401
- User isolation enforced

## 📁 Directory Structure
```
hackathon-todo/
├── .spec-kit/config.yaml
├── specs/
├── frontend/
├── backend/
├── CLAUDE.md
├── docker-compose.yml
└── README.md
```

## 🛠 Tools
- Next.js for frontend
- FastAPI for backend
- Better Auth with JWT
- SQLModel for database
- Neon PostgreSQL
- Tailwind CSS