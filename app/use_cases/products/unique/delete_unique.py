import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass

from fastapi_cache import FastAPICache

from app.services.unique_products import AbstractUniqueProductService
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

    unique_product_service: AbstractUniqueProductService

    async def execute(
        self,
        unique_product_id: int,
        uow: AbstractUnitOfWork,
    ) -> None:
        async with uow:
            product = await self.unique_product_service.get_one(
                uow=uow, conditions={"id": unique_product_id},
            )
            await self.unique_product_service.delete(id=unique_product_id, uow=uow)
            key = f"product:{hashlib.sha256(product.slug.encode()).hexdigest()}"
            await FastAPICache.get_backend().set(key, None, expire=1)
