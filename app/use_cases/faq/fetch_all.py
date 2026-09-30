from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.faq import ReadFAQSchema
from app.services.faq import AbstractFAQService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchFAQsUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        uow: AbstractUnitOfWork,
    ) -> list[ReadFAQSchema]: ...


@dataclass
class FetchFAQsUseCase(AbstractFetchFAQsUseCase):

    faq_service: AbstractFAQService

    async def execute(
        self,
        uow: AbstractUnitOfWork,
    ) -> list[ReadFAQSchema]:
        async with uow:
            return await self.faq_service.list_all(uow=uow)
