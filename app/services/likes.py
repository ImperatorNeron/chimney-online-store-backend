from abc import ABC, abstractmethod

from app.core.exceptions.common import ItemAlreadyExistsException
from app.schemas.likes import CreateLikeSchema, ReadLikeSchema
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractLikeService(ABC):

    @abstractmethod
    async def fetch_all(
        self,
        user_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[int]: ...

    @abstractmethod
    async def create(
        self,
        like_in: CreateLikeSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadLikeSchema: ...

    @abstractmethod
    async def delete(
        self,
        product_id: int,
        user_id: int,
        uow: AbstractUnitOfWork,
    ) -> None: ...


class LikeService(AbstractLikeService):

    async def fetch_all(
        self,
        user_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[int]:
        return await uow.like.all(user_id=user_id)

    async def create(
        self,
        like_in: CreateLikeSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadLikeSchema:
        like = await uow.like.get_or_none(**like_in.model_dump())
        if like is not None:
            raise ItemAlreadyExistsException()
        return await uow.like.create(item_in=like_in)

    async def delete(
        self,
        product_id: int,
        user_id: int,
        uow: AbstractUnitOfWork,
    ) -> None:
        return await uow.like.delete(product_id=product_id, user_id=user_id)
