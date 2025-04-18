from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.faq import CreateFAQSchema, ReadFAQSchema
from app.services.faq import AbstractFAQService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractCreateFAQUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        faq_in: CreateFAQSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadFAQSchema: ...


@dataclass
class CreateFAQUseCase(AbstractCreateFAQUseCase):

    faq_service: AbstractFAQService

    async def execute(
        self,
        faq_in: CreateFAQSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadFAQSchema:
        async with uow:
            return await self.faq_service.create(uow=uow, faq_in=faq_in)
