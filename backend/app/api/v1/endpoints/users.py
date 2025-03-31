from typing import Any, List
from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.api import deps
from app.schemas.user import User, UserCreate, UserUpdate, PasswordChange
from app.schemas.user import User, UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.db.session import get_db
from app.models.user import User as UserModel

router = APIRouter()


@router.get("/me", response_model=User)
async def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/", response_model=List[User])
async def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.

    Only available to superusers.
    """
    users_db = db.query(UserModel).offset(skip).limit(limit).all()

    # Convert to Pydantic models
    users = [
        User(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
        )
        for user in users_db
    ]

    return users


@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> Any:
    """
    Create new user via signup.
    """
    # Check if user with this email already exists
    user_exists = db.query(UserModel).filter(UserModel.email == user_in.email).first()
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create a new user with a hashed password
    db_user = UserModel(
        id=str(uuid.uuid4()),
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
        is_superuser=True,
        created_at=datetime.utcnow(),
    )

    # Save to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Convert to Pydantic model for response
    user = User(
        id=db_user.id,
        email=db_user.email,
        full_name=db_user.full_name,
        is_active=db_user.is_active,
        is_superuser=db_user.is_superuser,
        created_at=db_user.created_at,
    )

    return user


@router.post("/me/password", status_code=status.HTTP_200_OK)
async def change_password(
    *,
    db: Session = Depends(get_db),
    password_data: PasswordChange,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Change user password.
    """
    # Verify the current password
    db_user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
        
    if not verify_password(password_data.current_password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )
    
    # Update the password
    hashed_password = get_password_hash(password_data.new_password)
    db_user.hashed_password = hashed_password
    db.add(db_user)
    db.commit()
    
    return {"message": "Password updated successfully"}


@router.put("/me", response_model=User)
async def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user data.
    """
    # Get user from database
    db_user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update user attributes that were provided
    update_data = user_in.dict(exclude_unset=True)
    
    # If password is being updated, hash it
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # Don't allow regular users to change their superuser status
    if "is_superuser" in update_data and not current_user.is_superuser:
        del update_data["is_superuser"]
    
    # Apply updates to user model
    for field, value in update_data.items():
        if hasattr(db_user, field):
            setattr(db_user, field, value)
    
    # Commit changes to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Return updated user data
    return User(
        id=db_user.id,
        email=db_user.email,
        full_name=db_user.full_name,
        is_active=db_user.is_active,
        is_superuser=db_user.is_superuser,
        created_at=db_user.created_at,
    )
