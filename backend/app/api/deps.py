from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import ALGORITHM
from app.schemas.user import User
from app.schemas.document import TokenPayload
from app.db.session import get_db
from app.models.user import User as UserModel

settings = get_settings()

# Token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/access-token"
)

# API key authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get the current user based on JWT token.

    Args:
        db: Database session
        token: JWT token from Authorization header

    Returns:
        User object if token is valid

    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)

        if token_data.sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        # Get user from database
        user_db = db.query(UserModel).filter(UserModel.id == token_data.sub).first()
        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        # Convert to Pydantic schema
        user = User(
            id=user_db.id,
            email=user_db.email,
            full_name=user_db.full_name,
            is_active=user_db.is_active,
            is_superuser=user_db.is_superuser,
            created_at=user_db.created_at,
        )

        return user
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current active user.

    Args:
        current_user: User object from get_current_user dependency

    Returns:
        User object if user is active

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current active superuser.

    Args:
        current_user: User object from get_current_user dependency

    Returns:
        User object if user is active and superuser

    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user


async def get_api_key(
    db: Session = Depends(get_db),
    api_key: str = Security(api_key_header),
) -> Optional[str]:
    """
    Validate API key from header.

    Args:
        db: Database session
        api_key: API key from X-API-Key header

    Returns:
        API key if valid

    Raises:
        HTTPException: If API key is invalid
    """
    if api_key is None:
        return None

    # In a real app, you would validate the API key against a database here
    # For now, we'll keep this as a placeholder
    valid = True

    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return api_key


async def get_current_user_from_token_or_key(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
    api_key: Optional[str] = Depends(get_api_key),
) -> User:
    """
    Get current user from either token or API key.

    Args:
        db: Database session
        user: User from token authentication
        api_key: API key from header

    Returns:
        User object if either authentication method succeeds

    Raises:
        HTTPException: If neither authentication method succeeds
    """
    if user:
        return user

    if api_key:
        # In a real app, you would look up the user associated with this API key
        # This remains as a placeholder for future implementation
        # For now, let's use a fixed "api key user" as before
        api_key_user = User(
            id="api_key_user",
            email="api_user@example.com",
            is_active=True,
            is_superuser=False,
            full_name="API Key User",
            created_at=None,
        )
        return api_key_user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
    )
