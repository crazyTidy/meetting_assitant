"""User repository for external user system."""
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.dialects.sqlite import insert

from ..models.user_model import User


class UserRepository:
    """Repository for user data operations."""

    async def get_by_id(
        self,
        db: AsyncSession,
        user_id: str
    ) -> Optional[User]:
        """Get user by external ID."""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalars().first()

    async def get_or_update_user(
        self,
        db: AsyncSession,
        user_id: str,
        user_info: dict
    ) -> User:
        """
        Get user by ID or update/create with provided info.

        This method uses upsert logic to handle users from external system.

        Args:
            db: Database session
            user_id: External user ID
            user_info: User information dict (username, real_name, email, etc.)

        Returns:
            User instance
        """
        # Check if user exists
        user = await self.get_by_id(db, user_id)

        if user:
            # Update existing user
            update_data = {
                "username": user_info.get("username"),
                "real_name": user_info.get("real_name"),
                "email": user_info.get("email"),
                "phone": user_info.get("phone"),
                "department_id": user_info.get("department_id"),
                "department_name": user_info.get("department_name"),
                "position": user_info.get("position"),
                "last_seen_at": datetime.utcnow()
            }
            await db.execute(
                update(User)
                .where(User.id == user_id)
                .values(**{k: v for k, v in update_data.items() if v is not None})
            )
            await db.flush()
            # Refresh and return
            user = await self.get_by_id(db, user_id)
        else:
            # Create new user
            user = User(
                id=user_id,
                username=user_info.get("username"),
                real_name=user_info.get("real_name"),
                email=user_info.get("email"),
                phone=user_info.get("phone"),
                department_id=user_info.get("department_id"),
                department_name=user_info.get("department_name"),
                position=user_info.get("position"),
                last_seen_at=datetime.utcnow()
            )
            db.add(user)
            await db.flush()

        return user

    async def list(
        self,
        db: AsyncSession,
        limit: int = 100
    ) -> list:
        """List users."""
        result = await db.execute(
            select(User)
            .order_by(User.last_seen_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


# Singleton instance
user_repository = UserRepository()
