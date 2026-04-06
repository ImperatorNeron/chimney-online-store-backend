from __future__ import annotations

from datetime import datetime, timezone

import factory

from app.models.cart import Cart
from app.models.cart_item import CartItem


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CartFactory(factory.Factory):
    id = factory.Sequence(lambda n: n + 1)  # noqa
    user_id = None
    session_id = factory.Sequence(lambda n: f"{'s' * 31}{n % 10}")
    items = factory.LazyFunction(list)

    class Meta:
        model = Cart


class CartItemFactory(factory.Factory):
    id = factory.Sequence(lambda n: n + 1)  # noqa
    cart_id = 1
    product_id = 1
    quantity = 1
    cart = None
    product = None
    created_at = factory.LazyFunction(_now)
    updated_at = factory.LazyFunction(_now)

    class Meta:
        model = CartItem
