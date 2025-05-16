from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.products import (
    BaseCreateProductVariationSchema,
    CreateProductVariationSchema,
    ReadProductVariationSchema,
)
from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractCreateProductVariationsUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        unique_product_id: int,
        products_in: list[BaseCreateProductVariationSchema],
        uow: AbstractUnitOfWork,
    ) -> ReadProductVariationSchema: ...


@dataclass
class CreateProductVariationsUseCase(AbstractCreateProductVariationsUseCase):

    product_service: AbstractProductService

    async def execute(
        self,
        unique_product_id: int,
        products_in: list[BaseCreateProductVariationSchema],
        uow: AbstractUnitOfWork,
    ) -> ReadProductVariationSchema:
        async with uow:
            products = [
                CreateProductVariationSchema(
                    **product_in.model_dump(), product_id=unique_product_id,
                )
                for product_in in products_in
            ]
            return await self.product_service.create_variations(
                unique_product_id=unique_product_id,
                products_in=products,
                uow=uow,
            )
