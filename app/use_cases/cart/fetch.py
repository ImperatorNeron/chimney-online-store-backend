from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.mappers.carts import CartItemWithTotalPriceReadMapper
from app.schemas.carts import BaseCartSchema, ReadFullCartSchema
from app.services.cart_items import AbstractCartItemService
from app.services.carts import AbstractCartService
from app.services.website_settings import AbstractWebSiteSettingsService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchCartUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        uow: AbstractUnitOfWork,
        **kwargs: dict,
    ) -> ReadFullCartSchema: ...


@dataclass
class FetchCartUseCase(AbstractFetchCartUseCase):

    cart_service: AbstractCartService
    cart_item_service: AbstractCartItemService
    settings_service: AbstractWebSiteSettingsService

    # TODO: kwargs to explicit filtering
    async def execute(
        self,
        uow: AbstractUnitOfWork,
        cart_identifiers: BaseCartSchema,
    ) -> ReadFullCartSchema:
        async with uow:
            ws = await self.settings_service.get_settings(uow=uow)
            cart = await self.cart_service.get_one_with_settings(
                uow=uow, conditions=cart_identifiers, website_settings=ws,
            )
            total_quantity = self.cart_service.get_total_quantity(cart.items)
            items_with_total_amount = CartItemWithTotalPriceReadMapper.to_dto_list(
                cart.items,
            )
            total_price = self.cart_service.get_total_price(items_with_total_amount)
            return ReadFullCartSchema(
                id=cart.id,
                items=items_with_total_amount,
                total_price=total_price,
                total_quantity=total_quantity,
            )
