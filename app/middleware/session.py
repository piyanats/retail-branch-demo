"""Session management middleware"""

from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from fastapi import Request, HTTPException
from app.config import settings
from typing import Optional

# Initialize serializer with SECRET_KEY
serializer = URLSafeTimedSerializer(settings.SESSION_SECRET)

def create_session(user_data: dict) -> str:
    """
    Create signed session token

    Args:
        user_data: User data to store in session

    Returns:
        str: Signed session token
    """
    return serializer.dumps(user_data, salt='session-salt')

def verify_session(token: str) -> dict:
    """
    Verify and decode session token

    Args:
        token: Session token to verify

    Returns:
        dict: User data from session

    Raises:
        HTTPException: If session is invalid or expired
    """
    try:
        data = serializer.loads(
            token,
            salt='session-salt',
            max_age=settings.SESSION_MAX_AGE
        )
        return data
    except SignatureExpired:
        raise HTTPException(
            status_code=401,
            detail="Session expired. Please login again."
        )
    except BadSignature:
        raise HTTPException(
            status_code=401,
            detail="Invalid session. Please login again."
        )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )

def get_session_user(request: Request) -> Optional[dict]:
    """
    Get user from session cookie

    Args:
        request: FastAPI request object

    Returns:
        dict | None: User data if session is valid, None otherwise
    """
    session_token = request.cookies.get('session')

    if not session_token:
        return None

    try:
        return verify_session(session_token)
    except HTTPException:
        return None

def require_session(request: Request) -> dict:
    """
    Require valid session or raise error

    Args:
        request: FastAPI request object

    Returns:
        dict: User data from session

    Raises:
        HTTPException: If no valid session exists
    """
    user = get_session_user(request)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please login."
        )

    return user
