from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.website_settings import ReadWebSiteSettingsSchema, UpdateWebSiteSettingsSchema
from app.services.website_settings import AbstractWebSiteSettingsService
from app.use_cases.products._shared import invalidate_products_cache
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractUpdateWebSiteSettingsUseCase(ABC):

    @abstractmethod
    async def execute(
        self, item_in: UpdateWebSiteSettingsSchema, uow: AbstractUnitOfWork,
    ) -> ReadWebSiteSettingsSchema: ...


@dataclass
class UpdateWebSiteSettingsUseCase(AbstractUpdateWebSiteSettingsUseCase):

    settings_service: AbstractWebSiteSettingsService

    async def execute(
        self, item_in: UpdateWebSiteSettingsSchema, uow: AbstractUnitOfWork,
    ) -> ReadWebSiteSettingsSchema:
        async with uow:
            result = await self.settings_service.update_settings(item_in=item_in, uow=uow)
        await invalidate_products_cache()
        return result
