from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.website_settings import ReadWebSiteSettingsSchema
from app.services.website_settings import AbstractWebSiteSettingsService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchWebSiteSettingsUseCase(ABC):

    @abstractmethod
    async def execute(self, uow: AbstractUnitOfWork) -> ReadWebSiteSettingsSchema: ...


@dataclass
class FetchWebSiteSettingsUseCase(AbstractFetchWebSiteSettingsUseCase):

    settings_service: AbstractWebSiteSettingsService

    async def execute(self, uow: AbstractUnitOfWork) -> ReadWebSiteSettingsSchema:
        async with uow:
            return await self.settings_service.get_settings(uow=uow)
