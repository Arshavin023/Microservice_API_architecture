from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Any
from app.models.category import Category


class CategoryService:

    @staticmethod
    async def list_categories(db: AsyncSession, active_only: bool = True) -> list[Category]:
        query = select(Category).order_by(Category.display_order)
        if active_only:
            query = query.where(Category.is_active == True)  # noqa: E712
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_category(db: AsyncSession, category_id: str) -> Category | None:
        result = await db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_category(db: AsyncSession, data: dict[str, Any]) -> Category:
        category = Category(**data)
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def update_category(
        db: AsyncSession, category: Category, updates: dict[str, Any]
    ) -> Category:
        for field, value in updates.items():
            setattr(category, field, value)
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def delete_category(db: AsyncSession, category: Category) -> None:
        await db.delete(category)
        await db.commit()
