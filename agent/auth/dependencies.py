"""
Supabase JWT validation for FastAPI endpoints — via Supabase Auth API.

Every protected endpoint adds:
    current_user: dict = Depends(get_current_user)

The returned dict has keys: {"id": <uuid str>, "email": <str>}
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from agent.auth.supabase_client import get_supabase

bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> dict:
    try:
        response = get_supabase().auth.get_user(credentials.credentials)
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token.",
            )
        return {"id": response.user.id, "email": response.user.email or ""}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )
