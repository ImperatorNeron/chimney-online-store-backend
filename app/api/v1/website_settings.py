from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache

from app.api.v1.dependencies import get_current_active_auth_superuser
from app.core.containers import get_container
from app.core.settings import settings
from app.schemas.api_response import ApiResponseSchema
from app.schemas.website_settings import ReadWebSiteSettingsSchema, UpdateWebSiteSettingsSchema
from app.use_cases.website_settings.fetch import AbstractFetchWebSiteSettingsUseCase
from app.use_cases.website_settings.update import AbstractUpdateWebSiteSettingsUseCase
from app.utils.unit_of_work import AbstractUnitOfWork, UnitOfWork


router = APIRouter(prefix="/website-settings", tags=["WebSiteSettings"])


@router.get(
    "",
    response_model=ApiResponseSchema[ReadWebSiteSettingsSchema],
    dependencies=[Depends(get_current_active_auth_superuser)],
)
async def get_website_settings(
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchWebSiteSettingsUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchWebSiteSettingsUseCase)),
    ],
):
    return ApiResponseSchema(data=await use_case.execute(uow=uow))


@router.get(
    "/public",
    response_model=ApiResponseSchema[ReadWebSiteSettingsSchema],
)
@cache(expire=settings.cache.expire)
async def get_public_website_settings(
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchWebSiteSettingsUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchWebSiteSettingsUseCase)),
    ],
):
    return ApiResponseSchema(data=await use_case.execute(uow=uow))


@router.patch(
    "",
    response_model=ApiResponseSchema[ReadWebSiteSettingsSchema],
    dependencies=[Depends(get_current_active_auth_superuser)],
)
async def update_website_settings(
    item_in: UpdateWebSiteSettingsSchema,
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractUpdateWebSiteSettingsUseCase,
        Depends(lambda: get_container().resolve(AbstractUpdateWebSiteSettingsUseCase)),
    ],
):
    return ApiResponseSchema(data=await use_case.execute(item_in=item_in, uow=uow))
