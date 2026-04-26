from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.mappers.products import PreviewProductVariationReadMapper
from app.schemas.products import ReadPreviewProductSchema
from app.services.products import AbstractProductService
from app.services.website_settings import AbstractWebSiteSettingsService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchProductsByIdsUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        ids: list[int],
        uow: AbstractUnitOfWork,
    ) -> ReadPreviewProductSchema: ...


@dataclass
class FetchProductsByIdsUseCase(AbstractFetchProductsByIdsUseCase):

    product_service: AbstractProductService
    settings_service: AbstractWebSiteSettingsService

    async def execute(
        self,
        ids: list[int],
        uow: AbstractUnitOfWork,
    ) -> ReadPreviewProductSchema:
        async with uow:
            ws = await self.settings_service.get_settings(uow=uow)
            orm_objects = await uow.products.all(filters={"id__in": ids})
            return PreviewProductVariationReadMapper.to_dto_list(
                orm_objects, website_settings=ws,
            )
