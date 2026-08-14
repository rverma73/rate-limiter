from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import hash_password
from fastapi import HTTPException
from app.api.auth_dependencies import get_current_user
from app.services.auth import (
    verify_password,
    create_access_token
)
from app.database.redis import redis_client
from app.api.rate_limit_dependency import rate_limit
import json

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "healthy"}


@router.get("/api/data")
def get_data(
    username: str = Depends(rate_limit)
):
    return {
        "message": "This is protected API data",
        "user": username
    }


@router.post("/users", response_model=UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    hashed_password = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token(user.username)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/redis-test")
def redis_test():

    redis_client.set(
        "test_key",
        "Hello Redis"
    )

    value = redis_client.get("test_key")

    return {
        "value": value
    }


@router.get("/api/user/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    cache_key = f"user:{user_id}"

    # 1. Check Redis
    cached_user = redis_client.get(cache_key)

    if cached_user:
        return {
            "source": "redis",
            "data": json.loads(cached_user)
        }

    # 2. Cache miss → query PostgreSQL
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    data = {
        "id": user.id,
        "username": user.username
    }

    # 3. Store result in Redis for 60 seconds
    redis_client.setex(
        cache_key,
        60,
        json.dumps(data)
    )

    return {
        "source": "database",
        "data": data
    }

@router.put("/api/user/{user_id}")
def update_user(
    user_id: int,
    username: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.username = username
    db.commit()
    db.refresh(user)

    # Invalidate Redis cache
    redis_client.delete(f"user:{user_id}")

    return {
        "message": "User updated successfully"
    }



