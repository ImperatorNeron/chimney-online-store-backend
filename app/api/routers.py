from fastapi import APIRouter
from app.api.v1.routers import router as v1_router
from app.schemas.ping import PingResponseSchema


router = APIRouter(prefix="/api")
router.include_router(router=v1_router)


@router.get(
    "/ping",
    response_model=PingResponseSchema,
    tags=["Ping"],
)
async def ping():
    return PingResponseSchema(result=True)
