from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.products import ReadPreviewProductSchema
from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchProductsByIdsUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        ids: list[int],
        uow: AbstractUnitOfWork,
    ) -> ReadPreviewProductSchema: ...


@dataclass
class FetchProductsByIdsUseCase(AbstractFetchProductsByIdsUseCase):

    product_service: AbstractProductService

    async def execute(
        self,
        ids: list[int],
        uow: AbstractUnitOfWork,
    ) -> ReadPreviewProductSchema:
        async with uow:
            return await self.product_service.list_all(filters={"id__in": ids}, uow=uow)
