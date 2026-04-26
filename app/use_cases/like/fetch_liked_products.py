from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.api_response import ListPaginatedResponse
from app.schemas.filters import PaginationIn, PaginationOut
from app.schemas.products import ReadPreviewProductSchema
from app.services.likes import AbstractLikeService
from app.services.website_settings import AbstractWebSiteSettingsService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchLikedProductsUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        user_id: int,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> ListPaginatedResponse[ReadPreviewProductSchema]: ...


@dataclass
class FetchLikedProductsUseCase(AbstractFetchLikedProductsUseCase):
    like_service: AbstractLikeService
    settings_service: AbstractWebSiteSettingsService

    async def execute(
        self,
        user_id: int,
        pagination_in: PaginationIn,
        uow: AbstractUnitOfWork,
    ) -> ListPaginatedResponse[ReadPreviewProductSchema]:
        async with uow:
            ws = await self.settings_service.get_settings(uow=uow)
            items = await self.like_service.get_liked_products(
                user_id=user_id,
                uow=uow,
                limit=pagination_in.limit,
                offset=pagination_in.offset,
                website_settings=ws,
            )
            total = await self.like_service.count(
                uow=uow,
                filters={"user_id": user_id},
            )
            return ListPaginatedResponse(
                items=items,
                pagination=PaginationOut(
                    offset=pagination_in.offset,
                    limit=pagination_in.limit,
                    total=total,
                ),
            )
