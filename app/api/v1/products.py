import json
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import ValidationError

from app.core.containers import get_container
from app.core.exceptions.common import CustomPydanticValidationException
from app.schemas.api_response import ApiResponseSchema, ListPaginatedResponse
from app.schemas.filters import PaginationIn, ProductFiltersSchema, SortOrderSchema
from app.schemas.products import CreateProductSchema, ReadFullProductSchema, ReadPreviewProductSchema
from app.use_cases.products.create import AbstractCreateProductUseCase
from app.use_cases.products.fetch_all import AbstractFetchProductsUseCase
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


@router.get(
    "/{product_slug}",
    response_model=ApiResponseSchema[ReadFullProductSchema],
)
async def fetch_product(
    product_slug: str,
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchProductUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchProductUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(product_slug=product_slug, uow=uow),
    )


@router.post(
    "",
    response_model=ApiResponseSchema[ReadFullProductSchema],
)
async def create_product(
    # user: Annotated[ReadUserSchema, Depends(get_current_active_auth_superuser)],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractCreateProductUseCase,
        Depends(lambda: get_container().resolve(AbstractCreateProductUseCase)),
    ],
    images: list[UploadFile] = File(...),
    name: str = Form(...),
    slug: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    category_id: int = Form(...),
    characteristics: Optional[str] = Form(None),
):
    try:
        product_in = CreateProductSchema(
            name=name,
            slug=slug,
            description=description,
            price=price,
            category_id=category_id,
            characteristics=json.loads(characteristics) if characteristics else None,
        )
    except ValidationError as e:
        raise CustomPydanticValidationException(error=e)
    return ApiResponseSchema(
        data=await use_case.execute(
            product_in=product_in,
            images=images,
            uow=uow,
        ),
    )
