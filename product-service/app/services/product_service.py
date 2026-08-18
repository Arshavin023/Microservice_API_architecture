from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Any
from app.models.product import Product
from app.models.product_variant import ProductVariant


class ProductService:

    @staticmethod
    async def list_products(
        db: AsyncSession,
        category_id: str | None = None,
        available_only: bool = True,
    ) -> list[Product]:
        query = select(Product).options(selectinload(Product.variants))
        if available_only:
            query = query.where(Product.is_available == True)  # noqa: E712
        if category_id:
            query = query.where(Product.category_id == category_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_product(db: AsyncSession, product_id: str) -> Product | None:
        result = await db.execute(
            select(Product)
            .options(selectinload(Product.variants))
            .where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_product(db: AsyncSession, data: dict[str, Any]) -> Product:
        variants_data = data.pop("variants")
        product = Product(**data)
        db.add(product)
        await db.flush()
        for variant_data in variants_data:
            variant = ProductVariant(product_id=product.id, **variant_data)
            db.add(variant)
        await db.commit()
        await db.refresh(product)
        result = await ProductService.get_product(db, str(product.id))
        assert result is not None  # we just created it — guaranteed to exist
        return result

    @staticmethod
    async def update_product(
        db: AsyncSession, product: Product, updates: dict[str, Any]
    ) -> Product:
        for field, value in updates.items():
            setattr(product, field, value)
        await db.commit()
        await db.refresh(product)
        result = await ProductService.get_product(db, str(product.id))
        assert result is not None  # we just updated it — guaranteed to exist
        return result

    @staticmethod
    async def delete_product(db: AsyncSession, product: Product) -> None:
        await db.delete(product)
        await db.commit()
