import json
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from pydantic import ValidationError

from app.api.v1.dependencies import get_current_active_auth_superuser
from app.core.containers import get_container
from app.core.exceptions.common import CustomPydanticValidationException
from app.schemas.api_response import ApiResponseSchema, ListPaginatedResponse
from app.schemas.filters import PaginationIn, ProductFiltersSchema, SortOrderSchema
from app.schemas.products import (
    BaseCreateProductVariationSchema,
    CreateUniqueProductSchema,
    ReadAbsoluteProductSchema,
    ReadFiltersSchema,
    ReadFullUniqueProductSchema,
    ReadPreviewProductSchema,
    UpdateUniqueProductSchema,
    UpdateVariationSchema,
)
from app.use_cases.products.create import AbstractCreateProductUseCase
from app.use_cases.products.fetch_absolute_one import AbstractFetchAbsoluteProductUseCase
from app.use_cases.products.fetch_all import AbstractFetchProductsUseCase
from app.use_cases.products.fetch_by_ids import AbstractFetchProductsByIdsUseCase
from app.use_cases.products.fetch_filters import AbstractFetchFiltersUseCase
from app.use_cases.products.fetch_popular import AbstractFetchPopularProductsUseCase
from app.use_cases.products.unique.delete_unique import AbstractDeleteUniqueProductUseCase
from app.use_cases.products.unique.fetch_all import AbstractFetchUniqueProductsUseCase
from app.use_cases.products.update import AbstractUpdateProductUseCase
from app.utils.unit_of_work import AbstractUnitOfWork, UnitOfWork


router = APIRouter(prefix="/products", tags=["Products"])


# Read ======================================================
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


@router.get(
    "/unique",
    response_model=ApiResponseSchema[
        ListPaginatedResponse[ReadFullUniqueProductSchema]
    ],
)
async def get_unique_product_list(
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    pagination_in: Annotated[PaginationIn, Depends()],
    use_case: Annotated[
        AbstractFetchUniqueProductsUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchUniqueProductsUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(
            uow=uow,
            pagination_in=pagination_in,
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
    "/popular",
    response_model=ApiResponseSchema[ListPaginatedResponse[ReadPreviewProductSchema]],
)
async def get_products_recommendations(
    pagination_in: Annotated[PaginationIn, Depends()],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchPopularProductsUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchPopularProductsUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(
            uow=uow,
            pagination_in=pagination_in,
        ),
    )


@router.get(
    "/{product_slug}",
    response_model=ApiResponseSchema[ReadAbsoluteProductSchema],
)
async def fetch_absolute_product(
    product_slug: str,
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchAbsoluteProductUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchAbsoluteProductUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(
            product_slug=product_slug,
            uow=uow,
        ),
    )


# Create =====================================================================


@router.post(
    "/",
    response_model=ApiResponseSchema[ReadAbsoluteProductSchema],
    dependencies=[Depends(get_current_active_auth_superuser)],
)
async def create_product(
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractCreateProductUseCase,
        Depends(
            lambda: get_container().resolve(AbstractCreateProductUseCase),
        ),
    ],
    name: str = Form(...),
    slug: str = Form(...),
    description: Optional[str] = Form(None),
    category_id: int = Form(...),
    images: list[UploadFile] = File(...),
    variations_json: str = Form(...),
):
    try:
        product_in = CreateUniqueProductSchema(
            name=name,
            slug=slug,
            description=description,
            category_id=category_id,
        )
        variations = json.loads(variations_json)
        variations_in = [BaseCreateProductVariationSchema(**v) for v in variations]
    except ValidationError as e:
        raise CustomPydanticValidationException(error=e)
    return ApiResponseSchema(
        data=await use_case.execute(
            product_in=product_in,
            variations_in=variations_in,
            images=images,
            uow=uow,
        ),
    )


# Update =====================================================================


@router.patch(
    "/{product_id}",
    response_model=ApiResponseSchema[ReadAbsoluteProductSchema],
    dependencies=[Depends(get_current_active_auth_superuser)],
)
async def update_product(
    product_id: int,
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractUpdateProductUseCase,
        Depends(lambda: get_container().resolve(AbstractUpdateProductUseCase)),
    ],
    name: Optional[str] = Form(None),
    slug: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    new_images: Optional[list[UploadFile]] = File(None),
    delete_image_ids: Optional[str] = Form(None),
    variations_json: Optional[str] = Form(None),
):
    variations_in = []
    deleted_images = []
    try:
        product_in = UpdateUniqueProductSchema(
            name=name,
            slug=slug,
            description=description,
            category_id=int(category_id) if category_id else None,
        )
        product_in = UpdateUniqueProductSchema(
            **product_in.model_dump(exclude_none=True),
        )
        if delete_image_ids is not None:
            deleted_images = json.loads(delete_image_ids)
        if variations_json is not None:
            raw = json.loads(variations_json)
            variations_in = [UpdateVariationSchema(**v) for v in raw]
    except ValidationError as e:
        raise CustomPydanticValidationException(error=e)
    return ApiResponseSchema(
        data=await use_case.execute(
            product_id=product_id,
            product_in=product_in,
            variations=variations_in,
            images=new_images or [],
            delete_images_ids=deleted_images,
            uow=uow,
        ),
    )


# Delete =====================================================================


@router.delete(
    "/unique/{unique_product_id}",
    response_model=None,
    dependencies=[Depends(get_current_active_auth_superuser)],
)
async def delete_unique(
    unique_product_id: int,
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractDeleteUniqueProductUseCase,
        Depends(lambda: get_container().resolve(AbstractDeleteUniqueProductUseCase)),
    ],
):
    await use_case.execute(unique_product_id=unique_product_id, uow=uow)
