from fastapi import APIRouter, HTTPException, status, Depends, Header
from sqlmodel import Session, select
from typing import Optional
from datetime import datetime, timedelta
import jwt
from database import get_session
from models import User, UserCreate, UserRead
from settings import settings

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)


def create_jwt_token(user_id: str, email: str) -> str:
    """Create a JWT token for a user"""
    now = datetime.utcnow()
    payload = {
        "user_id": str(user_id),
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=settings.JWT_EXPIRATION_HOURS)).timestamp())
    }
    return jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)


@router.post("/signup", response_model=dict, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """
    Register a new user and return JWT token
    """
    try:
        # Check if user already exists
        existing_user = session.exec(
            select(User).where(User.email == user_data.email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        new_user = User(email=user_data.email)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        # Generate JWT token
        token = create_jwt_token(str(new_user.id), new_user.email)
        
        return {
            "token": token,
            "user": {
                "id": str(new_user.id),
                "email": new_user.email
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        # Log the full error for debugging
        import traceback
        error_details = traceback.format_exc()
        print(f"[AUTH ERROR] Signup failed: {e}")
        print(f"[AUTH ERROR] Full traceback:\n{error_details}")
        # Check if it's a constraint violation
        error_str = str(e)
        if "hashed_password" in error_str or "null value" in error_str.lower():
            print(f"[AUTH ERROR] Possible issue: hashed_password column in table but not in model!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


@router.post("/signin", response_model=dict)
async def signin(
    credentials: dict,
    session: Session = Depends(get_session)
):
    """
    Sign in with email and return JWT token
    For simplicity, we'll use email-only authentication (no password check)
    In production, you should verify passwords using bcrypt or similar
    """
    try:
        email = credentials.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        
        # Find user by email
        user = session.exec(
            select(User).where(User.email == email)
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or user not found"
            )
        
        # Generate JWT token
        token = create_jwt_token(str(user.id), user.email)
        
        return {
            "token": token,
            "user": {
                "id": str(user.id),
                "email": user.email
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error signing in: {str(e)}"
        )


@router.get("/me", response_model=dict)
async def get_current_user(
    authorization: Optional[str] = Header(None)
):
    """
    Get current user info from JWT token
    This endpoint is used to verify tokens and get user info
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        return {
            "id": payload["user_id"],
            "email": payload["email"]
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

