import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass

from fastapi_cache import FastAPICache

from app.core.constants import CACHED_PRODUCT_KEYS
from app.core.settings import settings
from app.schemas.api_response import ListPaginatedResponse
from app.schemas.filters import PaginationIn, PaginationOut, ProductFiltersSchema, SortOrderSchema
from app.schemas.products import ReadPreviewProductSchema
from app.services.products import AbstractProductService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractFetchProductsUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        filters: ProductFiltersSchema,
        sort_params: SortOrderSchema,
        uow: AbstractUnitOfWork,
        pagination_in: PaginationIn,
    ) -> ListPaginatedResponse[ReadPreviewProductSchema]: ...


@dataclass
class FetchProductsUseCase(AbstractFetchProductsUseCase):

    product_service: AbstractProductService

    async def execute(
        self,
        filters: ProductFiltersSchema,
        sort_params: SortOrderSchema,
        uow: AbstractUnitOfWork,
        pagination_in: PaginationIn,
    ) -> ListPaginatedResponse[ReadPreviewProductSchema]:
        key_data = {
            "filters": filters.model_dump(),
            "sort": sort_params.model_dump(),
            "pagination": pagination_in.model_dump(),
        }
        raw_key = json.dumps(key_data, sort_keys=True)
        key = "products:" + hashlib.sha256(raw_key.encode()).hexdigest()
        CACHED_PRODUCT_KEYS.add(key)
        cached = await FastAPICache.get_backend().get(key)
        if cached:
            return ListPaginatedResponse.model_validate_json(cached)

        async with uow:
            products = await self.product_service.list_product_previews(
                filters=filters,
                sort_params=sort_params,
                pagination_in=pagination_in,
                uow=uow,
            )
            count = await self.product_service.count(uow=uow, filters=filters)
            result = ListPaginatedResponse(
                items=products,
                pagination=PaginationOut(
                    offset=pagination_in.offset,
                    limit=pagination_in.limit,
                    total=count,
                ),
            )

        await FastAPICache.get_backend().set(
            key,
            result.model_dump_json(),
            expire=settings.cache.expire,
        )
        return result
