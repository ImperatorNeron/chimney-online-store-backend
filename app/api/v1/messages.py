from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.containers import get_container
from app.schemas.api_response import ApiResponseSchema, ListPaginatedResponse
from app.schemas.filters import PaginationIn
from app.schemas.messages import CreateMessageSchema, ReadMessageSchema
from app.use_cases.messages.create_messages import AbstractCreateMessageUseCase
from app.use_cases.messages.delete import AbstractDeleteMessageUseCase
from app.use_cases.messages.fetch_message import AbstractFetchMessageUseCase
from app.use_cases.messages.fetch_messages import AbstractFetchMessagesUseCase
from app.utils.unit_of_work import AbstractUnitOfWork, UnitOfWork


router = APIRouter(prefix="/messages", tags=["Messages"])


@router.get(
    "/",
    summary="Get list of messages",
    response_model=ApiResponseSchema[ListPaginatedResponse[ReadMessageSchema]],
)
async def get_messages_list(
    pagination_in: Annotated[PaginationIn, Depends()],
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchMessagesUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchMessagesUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(pagination_in=pagination_in, uow=uow),
    )


@router.get(
    "/{message_id}",
    summary="Get specific message by id",
    response_model=ApiResponseSchema[ReadMessageSchema],
)
async def get_message(
    message_id: int,
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchMessageUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchMessageUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(message_id=message_id, uow=uow),
    )


@router.post(
    "/",
    response_model=ApiResponseSchema[ReadMessageSchema],
    summary="Create new message",
)
async def create_message(
    message_in: CreateMessageSchema,
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractCreateMessageUseCase,
        Depends(lambda: get_container().resolve(AbstractCreateMessageUseCase)),
    ],
):
    return ApiResponseSchema(
        data=await use_case.execute(message_in=message_in, uow=uow),
    )


@router.delete(
    "/{message_id}",
    response_model=None,
    summary="Delete new message",
)
async def delete_message(
    message_id: int,
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractDeleteMessageUseCase,
        Depends(lambda: get_container().resolve(AbstractDeleteMessageUseCase)),
    ],
):
    await use_case.execute(
        message_id=message_id,
        uow=uow,
    )
