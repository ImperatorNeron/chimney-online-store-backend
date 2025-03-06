from fastapi import (
    APIRouter,
    Depends,
)

from app.api.v1.auth import router as auth
from app.api.v1.dependencies import http_bearer
from app.api.v1.users import router as users
from app.api.v1.messages import router as messages


router = APIRouter(prefix="/v1", dependencies=[Depends(http_bearer)])
router.include_router(router=auth)
router.include_router(router=users)
router.include_router(router=messages)
