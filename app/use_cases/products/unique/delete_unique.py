import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass

from fastapi_cache import FastAPICache

from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractDeleteUniqueProductUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        unique_product_id: int,
        uow: AbstractUnitOfWork,
    ) -> None: ...


@dataclass
class DeleteUniqueProductUseCase(AbstractDeleteUniqueProductUseCase):

    product_service: AbstractProductService

    async def execute(
        self,
        unique_product_id: int,
        uow: AbstractUnitOfWork,
    ) -> None:
        async with uow:
            product = await self.product_service.get_unique_product_by_id(product_id=unique_product_id, uow=uow)
            await self.product_service.delete_unique(
                unique_product_id=unique_product_id,
                uow=uow,
            )
            key = f"product:{hashlib.sha256(product.slug.encode()).hexdigest()}"
            await FastAPICache.get_backend().set(key, None, expire=1)
