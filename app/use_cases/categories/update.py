import logging
import os
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from fastapi import UploadFile

from app.core.exceptions.base import BaseAppException
from app.schemas.categories import ReadCategorySchema, UpdateCategorySchema
from app.services.categories import AbstractCategoryService
from app.services.files import AbstractFileStorageService
from app.utils.unit_of_work import AbstractUnitOfWork


logger = logging.getLogger(__name__)


class AbstractUpdateCategoryUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        category_id: int,
        category_in: UpdateCategorySchema,
        uow: AbstractUnitOfWork,
        image: Optional[UploadFile] = None,
        parent_slug: Optional[str] = None,
    ) -> ReadCategorySchema: ...


@dataclass
class UpdateCategoryUseCase(AbstractUpdateCategoryUseCase):

    category_service: AbstractCategoryService
    file_service: AbstractFileStorageService

    async def execute(
        self,
        category_id: int,
        category_in: UpdateCategorySchema,
        uow: AbstractUnitOfWork,
        image: Optional[UploadFile] = None,
        parent_slug: Optional[str] = None,
    ):
        async with uow:
            path: Optional[str] = None
            try:
                if image:
                    await self.file_service.verify_file(image)
                    current = await self.category_service.get_one(uow=uow, conditions={"id": category_id})
                    slug = category_in.slug or current.slug
                    path = self._get_category_image_path(image, slug, parent_slug)
                    await self.file_service.upload(image, path)
                    category_in = category_in.model_copy(update={"file_path": path})

                return await self.category_service.update(
                    item_id=category_id, item_in=category_in, uow=uow,
                )
            except BaseAppException:
                if path:
                    await self.file_service.cleanup_files([path])
                raise
            except Exception as e:
                if path:
                    await self.file_service.cleanup_files([path])
                logger.error("Failed to update category: %s", e, exc_info=True)
                raise

    @staticmethod
    def _get_category_image_path(file: UploadFile, slug: str, parent_slug: Optional[str] = None) -> str:
        ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4().hex}.{ext}"
        if parent_slug:
            return os.path.join("uploads", "categories", parent_slug, slug, filename)
        return os.path.join("uploads", "categories", slug, filename)
