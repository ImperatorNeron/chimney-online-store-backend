from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_current_active_auth_superuser
from app.core.containers import get_container
from app.schemas.api_response import ApiResponseSchema
from app.schemas.faq import CreateFAQSchema, ReadFAQSchema, UpdadeFAQSchema
from app.schemas.users import ReadUserSchema
from app.use_cases.faq.create import AbstractCreateFAQUseCase
from app.use_cases.faq.delete import AbstractDeleteFAQUseCase
from app.use_cases.faq.fetch_all import AbstractFetchFAQsUseCase
from app.use_cases.faq.fetch_one import AbstractFetchFAQUseCase
from app.use_cases.faq.update import AbstractUpdateFAQUseCase
from app.utils.unit_of_work import AbstractUnitOfWork, UnitOfWork


router = APIRouter(prefix="/faq", tags=["FAQ"])


@router.get(
    "",
    response_model=ApiResponseSchema[list[ReadFAQSchema]],
)
async def get_faqs_list(
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchFAQsUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchFAQsUseCase)),
    ],
):
    return ApiResponseSchema(data=await use_case.execute(uow=uow))


@router.get(
    "/{faq_id}",
    response_model=ApiResponseSchema[ReadFAQSchema],
)
async def get_faq(
    faq_id: int,
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchFAQUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchFAQUseCase)),
    ],
    _: Annotated[ReadUserSchema, Depends(get_current_active_auth_superuser)],
):
    return ApiResponseSchema(data=await use_case.execute(uow=uow, faq_id=faq_id))


@router.post(
    "",
    response_model=ApiResponseSchema[ReadFAQSchema],
)
async def create_faq(
    faq_in: CreateFAQSchema,
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractCreateFAQUseCase,
        Depends(lambda: get_container().resolve(AbstractCreateFAQUseCase)),
    ],
    _: Annotated[ReadUserSchema, Depends(get_current_active_auth_superuser)],
):
    return ApiResponseSchema(data=await use_case.execute(uow=uow, faq_in=faq_in))


@router.patch(
    "/{faq_id}",
    response_model=ApiResponseSchema[ReadFAQSchema],
)
async def update_faq(
    faq_id: int,
    faq_in: UpdadeFAQSchema,
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractUpdateFAQUseCase,
        Depends(lambda: get_container().resolve(AbstractUpdateFAQUseCase)),
    ],
    _: Annotated[ReadUserSchema, Depends(get_current_active_auth_superuser)],
):
    return ApiResponseSchema(
        data=await use_case.execute(
            uow=uow,
            faq_id=faq_id,
            faq_in=faq_in,
        ),
    )


@router.delete("/{faq_id}")
async def delete_faq(
    faq_id: int,
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractDeleteFAQUseCase,
        Depends(lambda: get_container().resolve(AbstractDeleteFAQUseCase)),
    ],
    _: Annotated[ReadUserSchema, Depends(get_current_active_auth_superuser)],
):
    return ApiResponseSchema(data=await use_case.execute(uow=uow, faq_id=faq_id))
