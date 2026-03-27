from abc import ABC, abstractmethod

from app.mappers.faq import FaqCreateMapper, FaqReadMapper, FaqUpdateMapper
from app.schemas.faq import CreateFAQSchema, ReadFAQSchema, UpdadeFAQSchema
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFAQService(ABC):

    @abstractmethod
    async def list_all(
        self,
        uow: AbstractUnitOfWork,
    ) -> list[ReadFAQSchema]: ...

    @abstractmethod
    async def get_one(
        self,
        faq_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadFAQSchema: ...

    @abstractmethod
    async def create(
        self,
        faq_in: CreateFAQSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadFAQSchema: ...

    @abstractmethod
    async def update(
        self,
        faq_in: UpdadeFAQSchema,
        faq_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadFAQSchema: ...

    @abstractmethod
    async def delete(
        self,
        faq_id: int,
        uow: AbstractUnitOfWork,
    ) -> None: ...


class FAQService(AbstractFAQService):

    async def list_all(
        self,
        uow: AbstractUnitOfWork,
    ) -> list[ReadFAQSchema]:
        return FaqReadMapper.to_dto_list(await uow.faq.all())

    async def get_one(
        self,
        faq_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadFAQSchema:
        return FaqReadMapper.to_dto(await uow.faq.get(id=faq_id))

    async def create(
        self,
        faq_in: CreateFAQSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadFAQSchema:
        return FaqReadMapper.to_dto(await uow.faq.create(item_in=FaqCreateMapper.to_model(faq_in)))

    async def update(
        self,
        faq_in: UpdadeFAQSchema,
        faq_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadFAQSchema:
        return FaqReadMapper.to_dto(await uow.faq.update(id=faq_id, item_in=FaqUpdateMapper.to_model(faq_in)))

    async def delete(
        self,
        faq_id: int,
        uow: AbstractUnitOfWork,
    ) -> None:
        return await uow.faq.delete(id=faq_id)
