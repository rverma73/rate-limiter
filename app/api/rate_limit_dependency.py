from fastapi import HTTPException, Depends

from app.api.auth_dependencies import get_current_user
from app.services.rate_limiter import allow_request


def rate_limit(
    username: str = Depends(get_current_user)
):
    allowed = allow_request(username)

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later."
        )

    return username