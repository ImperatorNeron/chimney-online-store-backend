from abc import ABC, abstractmethod

from app.schemas.filters import PaginationIn
from app.schemas.products import ReadPreviewProductSchema
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractProductService(ABC):

    @abstractmethod
    async def list_all(
        self,
        uow: AbstractUnitOfWork,
        pagination_in: PaginationIn,
    ) -> list[ReadPreviewProductSchema]: ...


class ProductService(AbstractProductService):
    async def list_all(
        self,
        uow: AbstractUnitOfWork,
        pagination_in: PaginationIn,
    ) -> list[ReadPreviewProductSchema]:
        return await uow.products.fetch_all_with_preview(pagination_in=pagination_in)
