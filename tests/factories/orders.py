from __future__ import annotations

from datetime import datetime, timezone

import factory
from factory import Faker

from app.models.orders import Order, OrderItem


def _now() -> datetime:
    return datetime.now(timezone.utc)


class OrderFactory(factory.Factory):
    id = factory.Sequence(lambda n: n + 1)  # noqa
    created_at = factory.LazyFunction(_now)
    updated_at = factory.LazyFunction(_now)
    user_id = None
    status = "pending"
    waybill_number = None
    price_discount = 0.0
    is_paid = False

    first_name = Faker("first_name")
    last_name = Faker("last_name")
    patronymic = Faker("first_name")
    phone_number = factory.Faker("numerify", text="0#########")
    email = Faker("email")
    address = Faker("street_address")
    shipping_method = "nova_poshta"
    payment_method = "cash"

    items = factory.LazyFunction(list)

    class Meta:
        model = Order


class OrderItemFactory(factory.Factory):
    id = factory.Sequence(lambda n: n + 1)  # noqa
    order_id = 1
    product_id = 1
    quantity = 1
    price_at_order = 10.0
    order = None
    product = None

    class Meta:
        model = OrderItem
