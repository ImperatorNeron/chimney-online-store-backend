from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.products import ReadFullProductWithCategoryHierarchySchema
from app.services.categories import AbstractCategoryService
from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchProductUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        product_slug: str,
        product_variation_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadFullProductWithCategoryHierarchySchema: ...


@dataclass
class FetchProductUseCase(AbstractFetchProductUseCase):

    product_service: AbstractProductService
    category_service: AbstractCategoryService

    async def execute(
        self,
        product_slug: str,
        product_variation_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadFullProductWithCategoryHierarchySchema:
        async with uow:
            result = await self.product_service.get_full_one(
                product_slug=product_slug,
                product_variation_id=product_variation_id,
                uow=uow,
            )
            categories = await self.category_service.get_category_hierarchy(
                category_id=result.category_id,
                uow=uow,
            )
            return ReadFullProductWithCategoryHierarchySchema(
                **result.model_dump(),
                categories=categories,
            )
