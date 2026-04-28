import logging
import os
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from fastapi import UploadFile

from app.core.exceptions.base import BaseAppException
from app.schemas.categories import CreateCategorySchema, ReadCategorySchema
from app.services.categories import AbstractCategoryService
from app.services.files import AbstractFileStorageService
from app.utils.unit_of_work import AbstractUnitOfWork


logger = logging.getLogger(__name__)


class AbstractCreateCategoryUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        category_in: CreateCategorySchema,
        uow: AbstractUnitOfWork,
        image: Optional[UploadFile] = None,
    ) -> ReadCategorySchema: ...


@dataclass
class CreateCategoryUseCase(AbstractCreateCategoryUseCase):

    category_service: AbstractCategoryService
    file_service: AbstractFileStorageService

    async def execute(
        self,
        category_in: CreateCategorySchema,
        uow: AbstractUnitOfWork,
        image: Optional[UploadFile] = None,
    ):
        async with uow:
            path: Optional[str] = None
            try:
                if image:
                    await self.file_service.verify_file(image)
                    path = self._get_category_image_path(image, category_in.slug)
                    await self.file_service.upload(image, path)
                    category_in = category_in.model_copy(update={"file_path": path})

                return await self.category_service.create(item_in=category_in, uow=uow)
            except BaseAppException:
                if path:
                    await self.file_service.cleanup_files([path])
                raise
            except Exception as e:
                if path:
                    await self.file_service.cleanup_files([path])
                logger.error("Failed to create category: %s", e, exc_info=True)
                raise

    # TODO: in file service probably we could add something like that and combine with products
    @staticmethod
    def _get_category_image_path(file: UploadFile, slug: str) -> str:
        ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4().hex}.{ext}"
        return os.path.join("uploads", "categories", slug, filename)
