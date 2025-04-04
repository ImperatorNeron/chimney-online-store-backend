from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.products import ReadFullProductSchema
from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchProductUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        product_slug: str,
        uow: AbstractUnitOfWork,
    ) -> ReadFullProductSchema: ...


@dataclass
class FetchProductUseCase(AbstractFetchProductUseCase):

    product_service: AbstractProductService

    async def execute(
        self,
        product_slug: str,
        uow: AbstractUnitOfWork,
    ) -> ReadFullProductSchema:
        async with uow:
            return await self.product_service.get_full_one(
                product_slug=product_slug,
                uow=uow,
            )
