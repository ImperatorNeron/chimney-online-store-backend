from app.mappers.base import BaseReadMapper, BaseUpsertMapper
from app.mappers.products import PreviewProductVariationReadMapper
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.schemas.cart_items import (
    CreateCartItemSchema,
    ReadCartItemSchema,
    ReadCartItemWithProductSchema,
    ReadCartItemWithTotalPriceSchema,
)
from app.schemas.carts import CreateCartSchema, ReadCartSchema


class CartItemReadMapper(BaseReadMapper[CartItem, ReadCartItemSchema]):
    @staticmethod
    def to_dto(orm_obj: CartItem) -> ReadCartItemSchema:
        return ReadCartItemSchema(
            id=orm_obj.id,
            cart_id=orm_obj.cart_id,
            quantity=orm_obj.quantity,
            product_id=orm_obj.product_id,
        )


class CartItemWithProductReadMapper(
    BaseReadMapper[
        CartItem,
        ReadCartItemWithProductSchema,
    ],
):
    @staticmethod
    def to_dto(orm_obj: CartItem) -> ReadCartItemWithProductSchema:
        return ReadCartItemWithProductSchema(
            id=orm_obj.id,
            cart_id=orm_obj.cart_id,
            quantity=orm_obj.quantity,
            product=PreviewProductVariationReadMapper.to_dto(orm_obj.product),
        )


class CartItemCreateMapper(BaseUpsertMapper[CartItem, CreateCartItemSchema]):
    pass


class CartReadMapper(BaseReadMapper[Cart, ReadCartSchema]):
    @staticmethod
    def to_dto(orm_obj: Cart) -> ReadCartSchema:
        return ReadCartSchema(id=orm_obj.id)


class CartWithItemsReadMapper(BaseReadMapper[Cart, ReadCartSchema]):
    @staticmethod
    def to_dto(orm_obj: Cart) -> ReadCartSchema:
        items = CartItemWithProductReadMapper.to_dto_list(orm_obj.items)
        return ReadCartSchema(id=orm_obj.id, items=items)


class CartCreateMapper(BaseUpsertMapper[Cart, CreateCartSchema]):
    pass


class CartItemWithTotalPriceReadMapper(
    BaseReadMapper[
        ReadCartItemWithProductSchema,
        ReadCartItemWithTotalPriceSchema,
    ],
):
    # It uses pydantic model, not orm one
    @staticmethod
    def to_dto(
        orm_obj: ReadCartItemWithProductSchema,
    ) -> ReadCartItemWithTotalPriceSchema:
        return ReadCartItemWithTotalPriceSchema(
            **orm_obj.model_dump(),
            total_price=orm_obj.quantity * orm_obj.product.discount_price,
        )
