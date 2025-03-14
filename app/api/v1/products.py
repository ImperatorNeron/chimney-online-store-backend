from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.containers import get_container
from app.schemas.api_response import ApiResponseSchema, ListPaginatedResponse
from app.schemas.filters import PaginationIn, PaginationOut
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
    pagination_in: Annotated[PaginationIn, Depends()],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchProductsUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchProductsUseCase)),
    ],
):
    # TODO: total should show how many rows in db
    return ApiResponseSchema(
        data=ListPaginatedResponse(
            items=await use_case.execute(pagination_in=pagination_in, uow=uow),
            pagination=PaginationOut(
                offset=pagination_in.offset,
                limit=pagination_in.limit,
                total=20,
            ),
        ),
    )


@router.get(
    "/{product_id}",
    response_model=ApiResponseSchema[ReadFullProductSchema],
)
async def fetch_product(
    product_id: int,
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchProductUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchProductUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(product_id=product_id, uow=uow),
    )


@router.post(
    "",
    response_model=ApiResponseSchema[ReadFullProductSchema],
)
async def create_product(
    images: Annotated[list[UploadFile], File(...)],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractCreateProductUseCase,
        Depends(lambda: get_container().resolve(AbstractCreateProductUseCase)),
    ],
    name: str = Form(...),
    slug: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    category_id: int = Form(...),
):
    return ApiResponseSchema(
        data=await use_case.execute(
            product_in=CreateProductSchema(
                name=name,
                slug=slug,
                description=description,
                price=price,
                category_id=category_id,
            ),
            images=images,
            uow=uow,
        ),
    )
