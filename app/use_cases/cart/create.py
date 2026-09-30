from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.carts import CreateCartSchema, ReadCartSchema
from app.services.carts import AbstractCartService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractCreateCartUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        uow: AbstractUnitOfWork,
        cart_in: CreateCartSchema,
    ) -> ReadCartSchema: ...


@dataclass
class CreateCartUseCase(AbstractCreateCartUseCase):

    cart_service: AbstractCartService

    async def execute(
        self,
        uow: AbstractUnitOfWork,
        cart_in: CreateCartSchema,
    ) -> ReadCartSchema:
        async with uow:
            return await self.cart_service.create(uow=uow, item_in=cart_in)
