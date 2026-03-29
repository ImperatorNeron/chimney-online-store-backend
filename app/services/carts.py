from abc import abstractmethod
from typing import Type

from app.mappers.carts import CartCreateMapper, CartReadMapper, CartWithItemsReadMapper
from app.schemas.cart_items import ReadCartItemWithProductSchema, ReadCartItemWithTotalPriceSchema
from app.schemas.carts import CreateCartSchema, ReadCartSchema
from app.services.base import AbstractCreate, AbstractDelete, AbstractRead, Create, Delete, Read


class AbstractCartService(
    AbstractRead[ReadCartSchema],
    AbstractCreate[ReadCartSchema, CreateCartSchema],
    AbstractDelete,
):

    @abstractmethod
    def get_total_quantity(self, items: list[ReadCartItemWithProductSchema]) -> int: ...

    @abstractmethod
    def get_total_price(
        self,
        items: list[ReadCartItemWithTotalPriceSchema],
    ) -> float: ...


class CartService(
    AbstractCartService,
    Read[ReadCartSchema],
    Create[ReadCartSchema, CreateCartSchema],
    Delete,
):
    repository_name: str = "cart"
    read_mapper: Type[CartWithItemsReadMapper] = CartWithItemsReadMapper
    read_create_mapper: Type[CartReadMapper] = CartReadMapper
    create_mapper: Type[CartCreateMapper] = CartCreateMapper

    def get_total_quantity(self, items: list[ReadCartItemWithProductSchema]) -> int:
        return sum(item.quantity for item in items)

    def get_total_price(self, items: list[ReadCartItemWithTotalPriceSchema]) -> float:
        return round(sum(item.total_price for item in items), 2)
