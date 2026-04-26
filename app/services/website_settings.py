from abc import ABC, abstractmethod
from typing import Type

from app.mappers.website_settings import WebSiteSettingsReadMapper, WebSiteSettingsUpdateMapper
from app.models.website_settings import WebSiteSettings
from app.schemas.website_settings import ReadWebSiteSettingsSchema, UpdateWebSiteSettingsSchema
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractWebSiteSettingsService(ABC):

    @abstractmethod
    async def get_settings(self, uow: AbstractUnitOfWork) -> ReadWebSiteSettingsSchema: ...

    @abstractmethod
    async def update_settings(
        self, item_in: UpdateWebSiteSettingsSchema, uow: AbstractUnitOfWork,
    ) -> ReadWebSiteSettingsSchema: ...


class WebSiteSettingsService(AbstractWebSiteSettingsService):
    read_mapper: Type[WebSiteSettingsReadMapper] = WebSiteSettingsReadMapper
    update_mapper: Type[WebSiteSettingsUpdateMapper] = WebSiteSettingsUpdateMapper

    async def _get_or_create(self, uow: AbstractUnitOfWork) -> WebSiteSettings:
        instance = await uow.website_settings.get_or_none(id=1)
        if instance is None:
            instance = await uow.website_settings.create(item_in=WebSiteSettings(id=1))
        return instance

    async def get_settings(self, uow: AbstractUnitOfWork) -> ReadWebSiteSettingsSchema:
        return self.read_mapper.to_dto(await self._get_or_create(uow))

    async def update_settings(
        self, item_in: UpdateWebSiteSettingsSchema, uow: AbstractUnitOfWork,
    ) -> ReadWebSiteSettingsSchema:
        await self._get_or_create(uow)
        updated = await uow.website_settings.update(
            id=1, item_in=self.update_mapper.to_model(item_in),
        )
        return self.read_mapper.to_dto(updated)
