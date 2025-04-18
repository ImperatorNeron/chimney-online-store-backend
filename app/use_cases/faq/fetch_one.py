from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.faq import ReadFAQSchema
from app.services.faq import AbstractFAQService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchFAQUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        faq_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadFAQSchema: ...


@dataclass
class FetchFAQUseCase(AbstractFetchFAQUseCase):

    faq_service: AbstractFAQService

    async def execute(
        self,
        faq_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadFAQSchema:
        async with uow:
            return await self.faq_service.get_one(uow=uow, faq_id=faq_id)
