from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import require_admin, get_current_active_user, require_role
from app.db.database import get_sync_db
from app.models.user import User, UserRole
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.services.user_service import UserService


router = APIRouter()


@router.post("/", response_model=UserSchema)
def create_user(
    *,
    db: Session = Depends(get_sync_db),
    user_in: UserCreate,
    current_user: User = Depends(require_admin)
) -> Any:
    """Create new user (Admin only)"""
    try:
        user = UserService.create_user(db=db, user_create=user_in)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[UserSchema])
def read_users(
    db: Session = Depends(get_sync_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role(UserRole.ANALYST)),
) -> Any:
    """Retrieve users (Analyst+ role required)"""
    users = UserService.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserSchema)
def read_user(
    *,
    db: Session = Depends(get_sync_db),
    user_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get user by ID"""
    # Users can only see their own profile unless they're admin/analyst
    if current_user.id != user_id and current_user.role not in [
        UserRole.ADMIN,
        UserRole.ANALYST,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    user = UserService.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    *,
    db: Session = Depends(get_sync_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Update user"""
    # Users can only update their own profile unless they're admin
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    # Non-admin users cannot change their role
    if (
        current_user.id == user_id
        and current_user.role != UserRole.ADMIN
        and user_in.role is not None
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Cannot change your own role"
        )

    user = UserService.update_user(db, user_id=user_id, user_update=user_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.delete("/{user_id}")
def delete_user(
    *,
    db: Session = Depends(get_sync_db),
    user_id: int,
    current_user: User = Depends(require_admin)
) -> Any:
    """Delete user (Admin only)"""
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself"
        )

    success = UserService.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return {"message": "User deleted successfully"}
