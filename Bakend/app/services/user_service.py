from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    """Service for user management operations"""

    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = (
            db.query(User)
            .filter(
                and_(
                    User.email == user_create.email,
                    User.username == user_create.username,
                )
            )
            .first()
        )

        if existing_user:
            raise ValueError("User with this email or username already exists")

        # Hash password
        hashed_password = get_password_hash(user_create.password)

        # Create user
        db_user = User(
            email=user_create.email,
            username=user_create.username,
            hashed_password=hashed_password,
            full_name=user_create.full_name,
            role=user_create.role,
            is_active=user_create.is_active,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/password"""
        user = UserService.get_user_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        return user

    @staticmethod
    def update_user(
        db: Session, user_id: int, user_update: UserUpdate
    ) -> Optional[User]:
        """Update user"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        update_data = user_update.dict(exclude_unset=True)

        # Hash password if provided
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(
                update_data.pop("password")
            )

        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete user (soft delete by deactivating)"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False

        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.commit()
        return True

    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
    ) -> List[User]:
        """Get users with filtering"""
        query = db.query(User)

        if role:
            query = query.filter(User.role == role)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def create_admin_user(
        db: Session, username: str, email: str, password: str, full_name: str = None
    ) -> User:
        """Create admin user"""
        user_create = UserCreate(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role=UserRole.ADMIN,
            is_active=True,
        )
        return UserService.create_user(db, user_create)
