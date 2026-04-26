from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.products import ReadDiscountedAdminSchema
from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchDiscountedAdminUseCase(ABC):

    @abstractmethod
    async def execute(self, uow: AbstractUnitOfWork) -> list[ReadDiscountedAdminSchema]: ...


@dataclass
class FetchDiscountedAdminUseCase(AbstractFetchDiscountedAdminUseCase):

    product_service: AbstractProductService

    async def execute(self, uow: AbstractUnitOfWork) -> list[ReadDiscountedAdminSchema]:
        async with uow:
            return await self.product_service.get_discounted_admin(uow=uow)
