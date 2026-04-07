"""
Supabase JWT validation for FastAPI endpoints.

Every protected endpoint adds:
    current_user: dict = Depends(get_current_user)

The returned dict has keys: {"id": <uuid str>, "email": <str>}
"""

import os

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

bearer = HTTPBearer()

SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "").strip()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> dict:
    if not SUPABASE_JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth not configured (SUPABASE_JWT_SECRET missing).",
        )
    try:
        payload = jwt.decode(
            credentials.credentials,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return {"id": payload["sub"], "email": payload.get("email", "")}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )
