from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
)


from app.api.v1.dependencies import get_current_active_auth_user
from app.schemas.users import (
    ReadUserSchema,
)


router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=ReadUserSchema,
)
async def get_authenticated_user_profile(
    user: Annotated[ReadUserSchema, Depends(get_current_active_auth_user)],
):
    return user
