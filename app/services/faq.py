from typing import Type

from app.mappers.faq import FaqCreateMapper, FaqReadMapper, FaqUpdateMapper
from app.schemas.faq import CreateFAQSchema, ReadFAQSchema, UpdadeFAQSchema
from app.services.base import AbstractCRUDService, CRUDService


class AbstractFAQService(AbstractCRUDService[ReadFAQSchema, CreateFAQSchema, UpdadeFAQSchema]):
    pass


# Maybe repository_name is not complitely good and maybe another class attrs could be passed somehow in init
class FAQService(AbstractFAQService, CRUDService):
    repository_name: str = "faq"
    _read_mapper: Type[FaqReadMapper] = FaqReadMapper
    read_mapper = read_create_mapper = read_update_mapper = _read_mapper
    create_mapper: Type[FaqCreateMapper] = FaqCreateMapper
    update_mapper: Type[FaqUpdateMapper] = FaqUpdateMapper
