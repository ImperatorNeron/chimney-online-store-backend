from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import factory
from factory import Faker

from app.models.product_images import ProductImage
from app.models.products import ProductVariation, UniqueProduct


def _now() -> datetime:
    return datetime.now(timezone.utc)


class UniqueProductFactory(factory.Factory):
    id = factory.Sequence(lambda n: n + 1)  # noqa
    created_at = factory.LazyFunction(_now)
    updated_at = factory.LazyFunction(_now)
    name = factory.Sequence(lambda n: f"Unique Product {n + 1}")
    slug = factory.Sequence(lambda n: f"unique-product-{n + 1}")
    description = None
    category_id = 1
    images = factory.LazyFunction(list)
    variations = factory.LazyFunction(list)

    class Meta:
        model = UniqueProduct


class ProductImageFactory(factory.Factory):
    id = factory.Sequence(lambda n: n + 1)  # noqa
    file_path = factory.Sequence(lambda n: f"uploads/unique-product-{n + 1}/img.jpg")
    alt = Faker("sentence", nb_words=3)
    product_id = 1
    product = None

    class Meta:
        model = ProductImage


class ProductVariationFactory(factory.Factory):
    id = factory.Sequence(lambda n: n + 1)  # noqa
    created_at = factory.LazyFunction(_now)
    updated_at = factory.LazyFunction(_now)
    product_id = 1
    price = 100.0
    discount_percentage = 0
    diameter = None
    length = None
    thickness = None
    angle = None
    metal_type = None
    extra_attrs = None
    product = None

    class Meta:
        model = ProductVariation


class ProductFiltersRepoResultFactory(factory.Factory):
    diameter = factory.LazyFunction(lambda: ["120"])
    length = factory.LazyFunction(lambda: ["250"])
    thickness = factory.LazyFunction(lambda: ["0.5"])
    angle = factory.LazyFunction(lambda: ["45"])
    metal_type = factory.LazyFunction(lambda: ["steel"])

    class Meta:
        model = SimpleNamespace
