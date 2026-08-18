# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from sqlalchemy.orm import selectinload
# from uuid import UUID
# from pydantic import BaseModel

# from app.db.session import get_db
# from app.core.auth import get_current_user_id, require_staff
# from app.models.order import Order, OrderStatus
# from app.schemas.order_schema import (
#     CartItemAdd, CartResponse, OrderResponse
# )
# from app.services.cart_service import CartService
# from app.services.order_service import OrderService, CheckoutError
# from app.utils.product_client import ProductServiceError

# router = APIRouter(tags=["Orders"])


# class StatusUpdate(BaseModel):
#     status: str


# def _parse_uuid(value: str, field: str = "id") -> UUID:
#     """Cast a path parameter string to UUID, returning 422 on malformed input."""
#     try:
#         return UUID(value)
#     except ValueError:
#         raise HTTPException(status_code=422, detail=f"Invalid {field} format")


# # ─── Cart endpoints ───────────────────────────────────────────────

# @router.get("/cart", response_model=CartResponse)
# async def get_cart(
#     user_id: UUID = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     """Get or create the active cart for the current user."""
#     cart = await CartService.get_or_create_cart(db, user_id)
#     return cart


# @router.post("/cart/items", response_model=CartResponse, status_code=201)
# async def add_to_cart(
#     item: CartItemAdd,
#     user_id: UUID = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     cart = await CartService.get_or_create_cart(db, user_id)
#     await CartService.add_item(
#         db, cart,
#         product_id=str(item.product_id),
#         variant_id=str(item.variant_id),
#         product_name=item.product_name,
#         size=item.size,
#         unit_price=item.unit_price,
#         quantity=item.quantity,
#     )
#     updated_cart = await CartService.get_active_cart(db, user_id)
#     return updated_cart


# @router.delete("/cart/items/{item_id}", status_code=204)
# async def remove_from_cart(
#     item_id: str,
#     user_id: UUID = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     uid = _parse_uuid(item_id, "item_id")
#     cart = await CartService.get_active_cart(db, user_id)
#     if not cart:
#         raise HTTPException(status_code=404, detail="No active cart found")
#     removed = await CartService.remove_item(db, cart, uid)
#     if not removed:
#         raise HTTPException(status_code=404, detail="Item not found in cart")


# # ─── Checkout ─────────────────────────────────────────────────────

# @router.post("/checkout", response_model=OrderResponse, status_code=201)
# async def checkout(
#     user_id: UUID = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     cart = await CartService.get_active_cart(db, user_id)
#     if not cart:
#         raise HTTPException(status_code=400, detail="No active cart to checkout")
#     if not cart.items:
#         raise HTTPException(status_code=400, detail="Cart is empty")
#     try:
#         order = await OrderService.checkout(db, cart, user_id)
#     except CheckoutError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except ProductServiceError as e:
#         raise HTTPException(status_code=503, detail=str(e))
#     return OrderResponse(
#         id=order.id,
#         status=order.status,
#         total_amount=order.total_amount,
#         items=order.items,
#         price_changes=getattr(order, "_price_changes", []),
#         authorization_url=getattr(order, "_authorization_url", None),
#         payment_reference=getattr(order, "_payment_reference", None),
#         created_at=order.created_at,
#         updated_at=order.updated_at,
#     )


# # ─── Order history ────────────────────────────────────────────────

# @router.get("/orders", response_model=list[OrderResponse])
# async def list_orders(
#     user_id: UUID = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     orders = await OrderService.list_orders(db, user_id)
#     return [
#         OrderResponse(
#             id=o.id,
#             status=o.status,
#             total_amount=o.total_amount,
#             items=o.items,
#             price_changes=[],
#             created_at=o.created_at,
#             updated_at=o.updated_at,
#         )
#         for o in orders
#     ]


# # ─── Staff: all orders ────────────────────────────────────────────
# # MUST come before /orders/{order_id} — FastAPI matches routes in order,
# # and "all" would otherwise be parsed as a UUID parameter (causing 422).

# @router.get("/orders/all", response_model=list[OrderResponse])
# async def get_all_orders(
#     db: AsyncSession = Depends(get_db),
#     _: None = Depends(require_staff),
# ):
#     """Staff-only — returns all active orders across all users."""
#     result = await db.execute(
#         select(Order)
#         .where(Order.status.in_([
#             OrderStatus.paid,
#             OrderStatus.shipped,
#             OrderStatus.awaiting_confirmation,
#         ]))
#         .options(selectinload(Order.items))
#         .order_by(Order.created_at.desc())
#     )
#     return result.scalars().all()


# # ─── Single order ─────────────────────────────────────────────────

# @router.get("/orders/{order_id}", response_model=OrderResponse)
# async def get_order(
#     order_id: str,
#     user_id: UUID = Depends(get_current_user_id),
#     db: AsyncSession = Depends(get_db),
# ):
#     uid = _parse_uuid(order_id, "order_id")
#     order = await OrderService.get_order(db, uid, user_id)
#     if not order:
#         raise HTTPException(status_code=404, detail="Order not found")
#     return OrderResponse(
#         id=order.id,
#         status=order.status,
#         total_amount=order.total_amount,
#         items=order.items,
#         price_changes=[],
#         created_at=order.created_at,
#         updated_at=order.updated_at,
#     )


# @router.patch("/orders/{order_id}/status")
# async def update_order_status(
#     order_id: str,
#     update: StatusUpdate,
#     db: AsyncSession = Depends(get_db),
# ):
#     """Internal — called by payment-service and workers. No JWT required."""
#     uid = _parse_uuid(order_id, "order_id")
#     try:
#         new_status = OrderStatus(update.status)
#     except ValueError:
#         raise HTTPException(status_code=400, detail=f"Invalid status: {update.status}")
#     result = await db.execute(select(Order).where(Order.id == uid))
#     order = result.scalar_one_or_none()
#     if not order:
#         raise HTTPException(status_code=404, detail="Order not found")
#     order.status = new_status
#     await db.commit()
#     return {"order_id": order_id, "status": new_status}


# @router.patch("/orders/{order_id}/confirm-delivery", response_model=OrderResponse)
# async def confirm_delivery(
#     order_id: str,
#     db: AsyncSession = Depends(get_db),
#     user_id: UUID = Depends(get_current_user_id),
# ):
#     """Customer confirms they received their order."""
#     uid = _parse_uuid(order_id, "order_id")
#     result = await db.execute(
#         select(Order).where(Order.id == uid, Order.user_id == user_id)
#     )
#     order = result.scalar_one_or_none()
#     if not order:
#         raise HTTPException(status_code=404, detail="Order not found")
#     if order.status.value != "awaiting_confirmation":
#         raise HTTPException(
#             status_code=409,
#             detail=f"Order cannot be confirmed — current status is '{order.status.value}'"
#         )
#     order.status = OrderStatus.delivered
#     await db.commit()
#     await db.refresh(order)
#     return order


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from pydantic import BaseModel

from app.db.session import get_db
from app.core.auth import get_current_user_id, require_staff
from app.models.order import Order, OrderStatus
from app.schemas.order_schema import CartItemAdd, CartResponse, OrderResponse
from app.services.cart_service import CartService
from app.services.order_service import OrderService, CheckoutError
from app.utils.product_client import ProductServiceError

router = APIRouter(tags=["Orders"])


class StatusUpdate(BaseModel):
    status: str


def _parse_uuid(value: str, field: str = "id") -> UUID:
    """Cast a path parameter string to UUID, returning 422 on malformed input."""
    try:
        return UUID(value)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid {field} format")


# ─── Cart endpoints ───────────────────────────────────────────────


@router.get("/cart", response_model=CartResponse)
async def get_cart(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get or create the active cart for the current user."""
    cart = await CartService.get_or_create_cart(db, user_id)
    return cart


@router.post("/cart/items", response_model=CartResponse, status_code=201)
async def add_to_cart(
    item: CartItemAdd,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    cart = await CartService.get_or_create_cart(db, user_id)
    await CartService.add_item(
        db,
        cart,
        product_id=str(item.product_id),
        variant_id=str(item.variant_id),
        product_name=item.product_name,
        size=item.size,
        unit_price=item.unit_price,
        quantity=item.quantity,
    )
    updated_cart = await CartService.get_active_cart(db, user_id)
    return updated_cart


@router.delete("/cart/items/{item_id}", status_code=204)
async def remove_from_cart(
    item_id: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    uid = _parse_uuid(item_id, "item_id")
    cart = await CartService.get_active_cart(db, user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="No active cart found")
    removed = await CartService.remove_item(db, cart, uid)
    if not removed:
        raise HTTPException(status_code=404, detail="Item not found in cart")


# ─── Checkout ─────────────────────────────────────────────────────


@router.post("/checkout", response_model=OrderResponse, status_code=201)
async def checkout(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    cart = await CartService.get_active_cart(db, user_id)
    if not cart:
        raise HTTPException(status_code=400, detail="No active cart to checkout")
    if not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    try:
        order = await OrderService.checkout(db, cart, user_id)
    except CheckoutError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ProductServiceError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return OrderResponse(
        id=order.id,
        status=order.status,
        total_amount=order.total_amount,
        items=order.items,
        price_changes=getattr(order, "_price_changes", []),
        authorization_url=getattr(order, "_authorization_url", None),
        payment_reference=getattr(order, "_payment_reference", None),
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


# ─── Order history ────────────────────────────────────────────────


@router.get("/orders", response_model=list[OrderResponse])
async def list_orders(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    orders = await OrderService.list_orders(db, user_id)
    return [
        OrderResponse(
            id=o.id,
            status=o.status,
            total_amount=o.total_amount,
            items=o.items,
            price_changes=[],
            created_at=o.created_at,
            updated_at=o.updated_at,
        )
        for o in orders
    ]


# ─── Staff: all orders ────────────────────────────────────────────


@router.get("/orders/all", response_model=list[OrderResponse])
async def get_all_orders(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_staff),
):
    """Staff-only — returns all active orders across all users."""
    result = await db.execute(
        select(Order)
        .where(
            Order.status.in_(
                [
                    OrderStatus.paid,
                    OrderStatus.shipped,
                    OrderStatus.awaiting_confirmation,
                ]
            )
        )
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )
    return result.scalars().all()


# ─── Single order ─────────────────────────────────────────────────


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    uid = _parse_uuid(order_id, "order_id")
    order = await OrderService.get_order(db, uid, user_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderResponse(
        id=order.id,
        status=order.status,
        total_amount=order.total_amount,
        items=order.items,
        price_changes=[],
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    update: StatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Internal — called by payment-service and workers. No JWT required."""
    uid = _parse_uuid(order_id, "order_id")
    try:
        new_status = OrderStatus(update.status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {update.status}")
    result = await db.execute(select(Order).where(Order.id == uid))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = new_status
    await db.commit()
    return {"order_id": order_id, "status": new_status}


@router.patch("/orders/{order_id}/confirm-delivery", response_model=OrderResponse)
async def confirm_delivery(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Customer confirms they received their order."""
    uid = _parse_uuid(order_id, "order_id")
    result = await db.execute(
        select(Order)
        .where(Order.id == uid, Order.user_id == user_id)
        .options(selectinload(Order.items))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status.value != "awaiting_confirmation":
        raise HTTPException(
            status_code=409,
            detail=f"Order cannot be confirmed — current status is '{order.status.value}'",
        )
    order.status = OrderStatus.delivered
    await db.commit()
    await db.refresh(order)  # <--- Re-populates expired scalar fields asynchronously

    return OrderResponse(
        id=order.id,
        status=order.status,
        total_amount=order.total_amount,
        items=order.items,
        price_changes=[],
        created_at=order.created_at,
        updated_at=order.updated_at,
    )
