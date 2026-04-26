from abc import abstractmethod
from typing import Type

from app.mappers.carts import CartCreateMapper, CartReadMapper, CartWithItemsReadMapper
from app.schemas.cart_items import ReadCartItemWithProductSchema, ReadCartItemWithTotalPriceSchema
from app.schemas.carts import CreateCartSchema, ReadCartSchema
from app.services.base import AbstractCreate, AbstractDelete, AbstractRead, Create, Delete, Read
from app.utils.unit_of_work import AbstractUnitOfWork


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

    @abstractmethod
    async def get_one_with_settings(
        self, uow: AbstractUnitOfWork, conditions, **kwargs,
    ) -> ReadCartSchema: ...


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
        return round(sum(item.total_price for item in items))

    async def get_one_with_settings(
        self, uow: AbstractUnitOfWork, conditions, **kwargs,
    ) -> ReadCartSchema:
        if isinstance(conditions, dict):
            orm_obj = await self._repository(uow).get(**conditions)
        else:
            orm_obj = await self._repository(uow).get(**conditions.model_dump())
        return self.read_mapper.to_dto(orm_obj, **kwargs)
