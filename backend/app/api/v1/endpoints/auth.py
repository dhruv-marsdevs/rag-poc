from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, verify_password, generate_api_key
from app.schemas.document import Token
from app.schemas.user import User, ApiKeyCreate, ApiKeyResponse
from app.api import deps
from app.models.user import User as UserModel

settings = get_settings()
router = APIRouter()


@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(deps.get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Find the user in the database by email
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()

    # Check if user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Create and return token
    return {
        "access_token": create_access_token(
            subject=user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/api-keys", response_model=ApiKeyResponse)
async def create_api_key(
    api_key_create: ApiKeyCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new API key for the current user.

    Note: In a real application, this would store the API key securely in a database.
    This example returns the key but doesn't actually store it.
    """
    # Generate a new API key
    full_key = generate_api_key()
    key_id = "key_" + full_key[:8]
    key_prefix = full_key[:8]

    # In a real application you would save the hashed key to the database

    # Return the full key (this is the only time it will be shown to the user)
    from datetime import datetime

    return ApiKeyResponse(
        id=key_id,
        name=api_key_create.name,
        api_key=full_key,
        prefix=key_prefix,
        created_at=datetime.utcnow(),
    )
