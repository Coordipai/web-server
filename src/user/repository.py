from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import User


async def create_user(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def find_user_by_github_id(db: AsyncSession, github_id: str) -> User | None:
    result = await db.execute(select(User).filter(User.github_id == github_id))
    return result.scalars().first()


async def find_user_by_user_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).filter(User.user_id == user_id))
    return result.scalars().first()
