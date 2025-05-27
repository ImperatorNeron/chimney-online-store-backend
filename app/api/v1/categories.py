from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi_cache.decorator import cache

from app.api.v1.dependencies import get_current_active_auth_superuser
from app.core.containers import get_container
from app.core.settings import settings
from app.schemas.api_response import ApiResponseSchema
from app.schemas.categories import CreateCategorySchema, ReadCategorySchema, UpdateCategorySchema
from app.use_cases.categories.create import AbstractCreateCategoryUseCase
from app.use_cases.categories.delete import AbstractDeleteCategoryUseCase
from app.use_cases.categories.fetch_all import AbstractFetchCategoriesUseCase
from app.use_cases.categories.get_names_from_slugs import AbstractFetchNamesFromSlugsUseCase
from app.use_cases.categories.update import AbstractUpdateCategoryUseCase
from app.utils.unit_of_work import AbstractUnitOfWork, UnitOfWork


router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=ApiResponseSchema[list[ReadCategorySchema]])
@cache(expire=settings.cache.expire)
async def get_categories_list(
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchCategoriesUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchCategoriesUseCase)),
    ],
):
    return ApiResponseSchema(data=await use_case.execute(uow=uow))


@router.get("/by-slugs", response_model=ApiResponseSchema[list[list[str, str]]])
async def get_categories_list_by_slugs(
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchNamesFromSlugsUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchNamesFromSlugsUseCase)),
    ],
    slugs: list[str] = Query(...),
):
    return ApiResponseSchema(data=await use_case.execute(slugs=slugs, uow=uow))


@router.post(
    "",
    response_model=ApiResponseSchema[ReadCategorySchema],
    dependencies=[Depends(get_current_active_auth_superuser)],
)
async def create_category(
    category_in: CreateCategorySchema,
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractCreateCategoryUseCase,
        Depends(lambda: get_container().resolve(AbstractCreateCategoryUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(
            category_in=category_in,
            uow=uow,
        ),
    )


@router.patch(
    "/{category_id}",
    response_model=ApiResponseSchema[ReadCategorySchema],
    dependencies=[Depends(get_current_active_auth_superuser)],
)
async def update_category(
    category_id: int,
    category_in: UpdateCategorySchema,
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractUpdateCategoryUseCase,
        Depends(lambda: get_container().resolve(AbstractUpdateCategoryUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(
            category_id=category_id,
            category_in=category_in,
            uow=uow,
        ),
    )


@router.delete(
    "/{category_id}",
    response_model=None,
    dependencies=[Depends(get_current_active_auth_superuser)],
)
async def delete_category(
    category_id: int,
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractDeleteCategoryUseCase,
        Depends(lambda: get_container().resolve(AbstractDeleteCategoryUseCase)),
    ],
):
    await use_case.execute(category_id=category_id, uow=uow)
