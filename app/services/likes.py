from abc import abstractmethod
from typing import Type

from app.core.exceptions.common import ItemAlreadyExistsException
from app.mappers.likes import LikeCreateMapper, LikeReadMapper
from app.mappers.products import PreviewProductVariationReadMapper
from app.schemas.likes import CreateLikeSchema, ReadLikeSchema
from app.schemas.products import ReadPreviewProductSchema
from app.schemas.website_settings import ReadWebSiteSettingsSchema
from app.services.base import AbstractCount, AbstractCreate, AbstractDelete, AbstractRead, Count, Create, Delete, Read
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractLikeService(
    AbstractRead[ReadLikeSchema],
    AbstractCreate[ReadLikeSchema, CreateLikeSchema],
    AbstractDelete,
    AbstractCount,
):
    @abstractmethod
    async def get_ids_list(self, user_id: int, uow: AbstractUnitOfWork) -> list[int]: ...

    @abstractmethod
    async def get_liked_products(
        self, user_id: int, uow: AbstractUnitOfWork, limit: int = 20, offset: int = 0,
        website_settings: ReadWebSiteSettingsSchema | None = None,
    ) -> list[ReadPreviewProductSchema]: ...


class LikeService(
    AbstractLikeService,
    Read[ReadLikeSchema],
    Create[ReadLikeSchema, CreateLikeSchema],
    Delete,
    Count,
):
    repository_name: str = "like"
    _read_mapper: Type[LikeReadMapper] = LikeReadMapper
    read_mapper = read_create_mapper = read_update_mapper = _read_mapper
    create_mapper: Type[LikeCreateMapper] = LikeCreateMapper

    async def get_ids_list(self, user_id: int, uow: AbstractUnitOfWork) -> list[int]:
        results = await self.list_all(filters={"user_id": user_id}, uow=uow)
        return [like.product_id for like in results]

    async def get_liked_products(
        self, user_id: int, uow: AbstractUnitOfWork, limit: int = 20, offset: int = 0,
        website_settings: ReadWebSiteSettingsSchema | None = None,
    ) -> list[ReadPreviewProductSchema]:
        products = await uow.like.get_liked_products(
            user_id=user_id, limit=limit, offset=offset,
        )
        return PreviewProductVariationReadMapper.to_dto_list(products, website_settings=website_settings)

    async def _create_validation(
        self,
        item_in: CreateLikeSchema,
        uow: AbstractUnitOfWork,
    ):
        like = await uow.like.get_or_none(**item_in.model_dump())
        if like is not None:
            raise ItemAlreadyExistsException()
