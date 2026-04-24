from fastapi import APIRouter, Depends

from app.api.v1.auth import router as auth
from app.api.v1.carts import router as carts
from app.api.v1.categories import router as categories
from app.api.v1.dependencies import http_bearer
from app.api.v1.faq import router as faqs
from app.api.v1.likes import router as likes
from app.api.v1.messages import router as messages
from app.api.v1.orders import router as orders
from app.api.v1.products import router as products
from app.api.v1.users import router as users


router = APIRouter(prefix="/v1", dependencies=[Depends(http_bearer)])
router.include_router(router=auth)
router.include_router(router=users)
router.include_router(router=messages)
router.include_router(router=categories)
router.include_router(router=products)
router.include_router(router=carts)
router.include_router(router=faqs)
router.include_router(router=likes)
router.include_router(router=orders)
