from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.services.faq import AbstractFAQService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractDeleteFAQUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        faq_id: int,
        uow: AbstractUnitOfWork,
    ) -> None: ...


@dataclass
class DeleteFAQUseCase(AbstractDeleteFAQUseCase):

    faq_service: AbstractFAQService

    async def execute(
        self,
        faq_id: int,
        uow: AbstractUnitOfWork,
    ) -> None:
        async with uow:
            return await self.faq_service.delete(uow=uow, id=faq_id)
