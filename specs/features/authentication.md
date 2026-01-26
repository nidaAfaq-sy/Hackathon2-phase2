# Authentication Feature Specification

## 🎯 Authentication Overview

### Better Auth Integration
- **Provider**: Better Auth handles user registration and login
- **JWT Plugin**: Enables JWT token exchange for API authentication
- **Session Management**: Automatic token storage and retrieval
- **Security**: HTTP-only cookies for token storage

## 🔐 Authentication Flow

### User Registration
```
1. User submits registration form
2. Better Auth validates email/password
3. User account created in database
4. JWT token issued and stored in cookie
5. User redirected to dashboard
```

### User Login
```
1. User submits login credentials
2. Better Auth validates credentials
3. JWT token issued and stored in cookie
4. User redirected to dashboard
```

### API Authentication
```
1. Frontend makes API request
2. JWT token automatically attached from cookie
3. Backend JWT middleware verifies token
4. User ID extracted from token
5. Route handler validates user authorization
```

## 📋 Authentication Endpoints

### Better Auth Routes (Handled by Library)
- **GET /api/auth/signin**: Login page
- **POST /api/auth/signin**: Submit login
- **GET /api/auth/signup**: Registration page
- **POST /api/auth/signup**: Submit registration
- **GET /api/auth/signout**: Logout
- **POST /api/auth/signout**: Submit logout
- **GET /api/auth/callback**: OAuth callback

### Custom Auth Routes
- **GET /api/auth/me**: Get current user info (JWT protected)

## 🔑 JWT Token Structure

### Token Payload
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "iat": 1234567890,
  "exp": 1234571490
}
```

### Token Security
- **Algorithm**: HS256
- **Secret**: BETTER_AUTH_SECRET environment variable
- **Expiration**: 24 hours
- **Storage**: HTTP-only cookie (secure)

## 🛡️ Security Requirements

### JWT Verification
- **Middleware**: All protected routes require JWT verification
- **Algorithm**: HS256 with BETTER_AUTH_SECRET
- **Expiration**: Automatic handling of expired tokens
- **Errors**: 401 Unauthorized for invalid/missing tokens

### User Authorization
- **User ID Match**: JWT user_id must match URL user_id
- **Error Handling**: 403 Forbidden for user mismatch
- **Database Isolation**: Queries filtered by user_id

### Session Management
- **Automatic**: Better Auth handles session lifecycle
- **Secure Cookies**: HTTP-only, secure flags enabled
- **CSRF Protection**: Built into Better Auth

## 📱 Frontend Integration

### Better Auth Provider
```tsx
// Wrap entire application
<BetterAuthProvider>
  <App />
</BetterAuthProvider>
```

### Session Access
```tsx
// Get current user
const { session, signIn, signOut } = useSession();
```

### Protected Routes
```tsx
// Middleware for protected pages
export const metadata = {
  middleware: {
    protected: true,
  },
};
```

## 🔧 Configuration

### Environment Variables
```env
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000
```

### Better Auth Setup
```typescript
// auth.ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  database: {
    // Database configuration
  },
  jwt: {
    enabled: true,
    secret: process.env.BETTER_AUTH_SECRET!,
  },
});
```

## 🚨 Error Handling

### Authentication Errors
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: JWT user_id doesn't match URL user_id
- **422 Unprocessable Entity**: Invalid form data

### Common Issues
- **Token Expiration**: Automatic redirect to login
- **Invalid Credentials**: Clear error messages
- **Network Errors**: Graceful handling with retry logic