from abc import abstractmethod
from typing import Type

from app.core.exceptions.common import ItemAlreadyExistsException
from app.mappers.likes import LikeCreateMapper, LikeReadMapper
from app.schemas.likes import CreateLikeSchema, ReadLikeSchema
from app.services.base import AbstractCreate, AbstractDelete, AbstractRead, Create, Delete, Read
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractLikeService(
    AbstractRead[ReadLikeSchema],
    AbstractCreate[ReadLikeSchema, CreateLikeSchema],
    AbstractDelete,
):
    @abstractmethod
    async def get_ids_list(self, user_id: int, uow: AbstractUnitOfWork) -> list[int]:
        pass


class LikeService(
    AbstractLikeService,
    Read[ReadLikeSchema],
    Create[ReadLikeSchema, CreateLikeSchema],
    Delete,
):
    repository_name: str = "like"
    read_mapper: Type[LikeReadMapper] = LikeReadMapper
    create_mapper: Type[LikeCreateMapper] = LikeCreateMapper

    async def get_ids_list(self, user_id: int, uow: AbstractUnitOfWork) -> list[int]:
        results = await self.list_all(filters={"user_id": user_id}, uow=uow)
        return [like.product_id for like in results]

    async def _create_validation(
        self,
        item_in: CreateLikeSchema,
        uow: AbstractUnitOfWork,
    ):
        like = await uow.like.get_or_none(**item_in.model_dump())
        if like is not None:
            raise ItemAlreadyExistsException()
