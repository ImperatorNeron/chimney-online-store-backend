from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.filters import PaginationIn
from app.schemas.products import ReadPreviewProductSchema
from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchProductsUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        uow: AbstractUnitOfWork,
        pagination_in: PaginationIn,
    ) -> list[ReadPreviewProductSchema]: ...


@dataclass
class FetchProductsUseCase(AbstractFetchProductsUseCase):

    product_service: AbstractProductService

    async def execute(
        self,
        uow: AbstractUnitOfWork,
        pagination_in: PaginationIn,
    ) -> list[ReadPreviewProductSchema]:
        async with uow:
            return await self.product_service.list_all(
                pagination_in=pagination_in,
                uow=uow,
            )
