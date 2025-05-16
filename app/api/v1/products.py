from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from pydantic import ValidationError

from app.core.containers import get_container
from app.core.exceptions.common import CustomPydanticValidationException
from app.schemas.api_response import ApiResponseSchema, ListPaginatedResponse
from app.schemas.filters import PaginationIn, ProductFiltersSchema, SortOrderSchema
from app.schemas.products import (
    BaseCreateProductVariationSchema,
    CreateUniqueProductSchema,
    ReadFiltersSchema,
    ReadFullProductSchema,
    ReadPreviewProductSchema,
    ReadProductVariationSchema,
    ReadUniqueProductSchema,
)
from app.use_cases.products.create_unique import AbstractCreateUniqueProductUseCase
from app.use_cases.products.create_variations import AbstractCreateProductVariationsUseCase
from app.use_cases.products.fetch_all import AbstractFetchProductsUseCase
from app.use_cases.products.fetch_by_ids import AbstractFetchProductsByIdsUseCase
from app.use_cases.products.fetch_filters import AbstractFetchFiltersUseCase
from app.use_cases.products.fetch_one import AbstractFetchProductUseCase
from app.utils.unit_of_work import AbstractUnitOfWork, UnitOfWork


router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    "",
    response_model=ApiResponseSchema[ListPaginatedResponse[ReadPreviewProductSchema]],
)
async def get_products_list(
    filters: Annotated[ProductFiltersSchema, Depends()],
    sort_params: Annotated[SortOrderSchema, Depends()],
    pagination_in: Annotated[PaginationIn, Depends()],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchProductsUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchProductsUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(
            uow=uow,
            filters=filters,
            sort_params=sort_params,
            pagination_in=pagination_in,
        ),
    )


@router.get("/by-ids", response_model=ApiResponseSchema[list[ReadPreviewProductSchema]])
async def get_products_by_likes_list(
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchProductsByIdsUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchProductsByIdsUseCase)),
    ],
    product_ids: list[int] = Query(default=[]),
):
    return ApiResponseSchema(data=await use_case.execute(ids=product_ids, uow=uow))


@router.post("", response_model=ApiResponseSchema[ReadUniqueProductSchema])
async def create_unique(
    # user: Annotated[ReadUserSchema, Depends(get_current_active_auth_superuser)],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractCreateUniqueProductUseCase,
        Depends(lambda: get_container().resolve(AbstractCreateUniqueProductUseCase)),
    ],
    name: str = Form(...),
    slug: str = Form(...),
    description: Optional[str] = Form(None),
    category_id: int = Form(...),
    images: list[UploadFile] = File(...),
):
    try:
        product_in = CreateUniqueProductSchema(
            name=name,
            slug=slug,
            description=description,
            category_id=category_id,
        )
    except ValidationError as e:
        raise CustomPydanticValidationException(error=e)
    return ApiResponseSchema(
        data=await use_case.execute(
            product_in=product_in,
            uow=uow,
            images=images,
        ),
    )


@router.post(
    "/{unique_product_id}",
    response_model=ApiResponseSchema[list[ReadProductVariationSchema]],
)
async def create_variations(
    # user: Annotated[ReadUserSchema, Depends(get_current_active_auth_superuser)],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractCreateProductVariationsUseCase,
        Depends(
            lambda: get_container().resolve(AbstractCreateProductVariationsUseCase),
        ),
    ],
    unique_product_id: int,
    products_in: list[BaseCreateProductVariationSchema],
):
    return ApiResponseSchema(
        data=await use_case.execute(
            unique_product_id=unique_product_id,
            products_in=products_in,
            uow=uow,
        ),
    )


@router.get(
    "/filters",
    response_model=ApiResponseSchema[ReadFiltersSchema],
)
async def fetch_filters(
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchFiltersUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchFiltersUseCase)),
    ],
    slug: Optional[str] = Query(default=None),
    text: Optional[str] = Query(default=None),
):

    return ApiResponseSchema(data=await use_case.execute(slug=slug, text=text, uow=uow))


@router.get(
    "/{product_slug}/{product_variation_id}",
    response_model=ApiResponseSchema[ReadFullProductSchema],
)
async def fetch_product(
    product_slug: str,
    product_variation_id: int,
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchProductUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchProductUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(
            product_slug=product_slug,
            product_variation_id=product_variation_id,
            uow=uow,
        ),
    )
