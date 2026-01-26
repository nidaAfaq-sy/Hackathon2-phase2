from fastapi import Request, HTTPException
from fastapi.security.utils import get_authorization_scheme_param
import jwt
from jwt.exceptions import PyJWTError
from typing import Optional, Dict, Any
from pydantic import BaseModel
from settings import settings

def get_cors_headers() -> list:
    """Get CORS headers from settings"""
    # Allow all origins from settings, or default to localhost:3000
    allowed_origins = getattr(settings, 'ALLOWED_ORIGINS', ['http://localhost:3000'])
    # For simplicity, we'll allow the first origin or localhost:3000
    origin = allowed_origins[0] if allowed_origins else 'http://localhost:3000'
    return [
        (b"access-control-allow-origin", origin.encode()),
        (b"access-control-allow-credentials", b"true"),
        (b"access-control-allow-methods", b"GET, POST, PUT, DELETE, OPTIONS, PATCH"),
        (b"access-control-allow-headers", b"Content-Type, Authorization, X-Requested-With"),
    ]


class JWTPayload(BaseModel):
    """JWT token payload schema"""
    user_id: str
    email: str
    iat: int
    exp: int


class JWTAuthMiddleware:
    """JWT authentication middleware for FastAPI"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)

        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            await self.app(scope, receive, send)
            return

        # Skip authentication for auth routes
        if request.url.path.startswith("/api/auth"):
            await self.app(scope, receive, send)
            return

        # Extract JWT token from Authorization header
        token = self.extract_jwt_token(request)

        if not token:
            # Return 401 Unauthorized
            await self.handle_unauthorized(send)
            return

        # Verify JWT token
        try:
            payload = self.verify_jwt_token(token)
            # Add user info to request state for later use
            request.state.user = payload
        except HTTPException as e:
            await self.handle_error(send, e.status_code, e.detail)
            return

        await self.app(scope, receive, send)

    def extract_jwt_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from Authorization header"""
        authorization: str = request.headers.get("Authorization")
        if not authorization:
            return None

        scheme, token = get_authorization_scheme_param(authorization)
        if scheme.lower() != "bearer":
            return None

        return token

    def verify_jwt_token(self, token: str) -> JWTPayload:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.BETTER_AUTH_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return JWTPayload(**payload)
        except PyJWTError:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def handle_unauthorized(self, send):
        """Handle unauthorized requests"""
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
            ] + get_cors_headers(),
        })
        await send({
            "type": "http.response.body",
            "body": b'{"error": "Unauthorized", "message": "Authentication required"}',
        })

    async def handle_error(self, send, status_code: int, detail: str):
        """Handle authentication errors"""
        await send({
            "type": "http.response.start",
            "status": status_code,
            "headers": [
                (b"content-type", b"application/json"),
            ] + get_cors_headers(),
        })
        await send({
            "type": "http.response.body",
            "body": f'{{"error": "Authentication Error", "message": "{detail}"}}'.encode(),
        })


def verify_jwt_token(token: str) -> JWTPayload:
    """Verify JWT token (utility function)"""
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return JWTPayload(**payload)
    except PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def extract_user_id_from_token(token: str) -> str:
    """Extract user ID from JWT token"""
    payload = verify_jwt_token(token)
    return payload.user_id


def validate_user_authorization(token: str, user_id: str) -> bool:
    """Validate that JWT token belongs to the specified user"""
    try:
        payload = verify_jwt_token(token)
        return payload.user_id == user_id
    except HTTPException:
        return False