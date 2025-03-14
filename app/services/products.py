from abc import ABC, abstractmethod

from app.schemas.filters import PaginationIn
from app.schemas.products import CreateProductSchema, ReadFullProductSchema, ReadPreviewProductSchema, ReadProductSchema
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractProductService(ABC):

    @abstractmethod
    async def list_all(
        self,
        uow: AbstractUnitOfWork,
        pagination_in: PaginationIn,
    ) -> list[ReadPreviewProductSchema]: ...

    @abstractmethod
    async def get_full_one(
        self,
        product_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadFullProductSchema: ...

    @abstractmethod
    async def create(
        self,
        product_in: CreateProductSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadProductSchema: ...


class ProductService(AbstractProductService):
    async def list_all(
        self,
        uow: AbstractUnitOfWork,
        pagination_in: PaginationIn,
    ) -> list[ReadPreviewProductSchema]:
        return await uow.products.fetch_all_with_preview(pagination_in=pagination_in)

    async def get_full_one(
        self,
        product_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadFullProductSchema:
        return await uow.products.fetch_full_one_by_id(product_id=product_id)

    async def create(
        self,
        product_in: CreateProductSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadProductSchema:
        return await uow.products.create(item_in=product_in)
