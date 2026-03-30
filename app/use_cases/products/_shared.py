import logging
from collections.abc import Iterable, Sequence

from fastapi import UploadFile
from fastapi_cache import FastAPICache

from app.core.constants import CACHED_PRODUCT_KEYS
from app.core.exceptions.base import BaseAppException
from app.core.exceptions.common import ProductCreationException
from app.schemas.product_images import CreateProductImageSchema, ReadProductImageSchema
from app.services.files import AbstractFileStorageService
from app.services.product_images import AbstractProductImageService
from app.utils.unit_of_work import AbstractUnitOfWork


async def upload_and_create_product_images(
    *,
    images: Sequence[UploadFile],
    product_id: int,
    product_slug: str,
    alt: str,
    file_service: AbstractFileStorageService,
    product_image_service: AbstractProductImageService,
    uow: AbstractUnitOfWork,
    logger: logging.Logger,
    log_error_message: str,
) -> list[ReadProductImageSchema]:
    # TODO: after create/update it would be cool to delete photos in bucket
    image_data: list[CreateProductImageSchema] = []
    try:
        for img in images:
            await file_service.verify_file(img)
            path = file_service.get_path(img, product_slug)
            await file_service.upload(img, path)
            image_data.append(
                CreateProductImageSchema(
                    file_path=path,
                    alt=alt,
                    product_id=product_id,
                ),
            )
        if not image_data:
            return []
        return await product_image_service.bulk_create(images=image_data, uow=uow)
    except BaseAppException:
        await file_service.cleanup_files(image_data)
        raise
    except Exception as e:
        logger.error(log_error_message, e, exc_info=True)
        await file_service.cleanup_files(image_data)
        # TODO: change it for update/create
        raise ProductCreationException()


async def invalidate_products_cache(*, extra_keys: Iterable[str] = ()) -> None:
    backend = FastAPICache.get_backend()
    for key in (*CACHED_PRODUCT_KEYS, *extra_keys):
        await backend.set(key, None, expire=1)
    CACHED_PRODUCT_KEYS.clear()
