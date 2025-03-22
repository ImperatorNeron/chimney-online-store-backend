from typing import Annotated, Optional

from fastapi import APIRouter, Depends

from app.core.containers import get_container
from app.schemas.api_response import ApiResponseSchema
from app.schemas.carts import ReadFullCartSchema
from app.use_cases.cart.fetch import AbstractFetchCartUseCase
from app.utils.unit_of_work import AbstractUnitOfWork, UnitOfWork


router = APIRouter(prefix="/carts", tags=["Carts"])


@router.get("", response_model=ApiResponseSchema[ReadFullCartSchema])
async def get_cart(
    uow: Annotated[AbstractUnitOfWork, Depends(UnitOfWork)],
    use_case: Annotated[
        AbstractFetchCartUseCase,
        Depends(lambda: get_container().resolve(AbstractFetchCartUseCase)),
    ],
    user_id: Optional[int] = None,
    session_id: Optional[str] = None,
):
    # TODO: обробити запит і дізнати що передалося. Це пробна реалізація.
    return ApiResponseSchema(
        data=await use_case.execute(
            user_id=user_id,
            uow=uow,
        ),
    )
