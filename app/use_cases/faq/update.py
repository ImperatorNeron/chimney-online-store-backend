from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.faq import ReadFAQSchema, UpdadeFAQSchema
from app.services.faq import AbstractFAQService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractUpdateFAQUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        faq_id: int,
        faq_in: UpdadeFAQSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadFAQSchema: ...


@dataclass
class UpdateFAQUseCase(AbstractUpdateFAQUseCase):

    faq_service: AbstractFAQService

    async def execute(
        self,
        faq_id: int,
        faq_in: UpdadeFAQSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadFAQSchema:
        async with uow:
            return await self.faq_service.update(uow=uow, item_id=faq_id, item_in=faq_in)
