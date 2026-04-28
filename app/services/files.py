import logging
import os
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

import aiofiles
import aiofiles.os
import magic
from fastapi import UploadFile

from app.core.exceptions.common import (
    FileDeletionException,
    FileTooLargeException,
    FileUploadException,
    UnsupportedMediaException,
)
from app.core.settings import settings
from app.core.supabase import supabase_client


logger = logging.getLogger(__name__)


class AbstractFileStorageService(ABC):

    @abstractmethod
    async def upload(self, file: UploadFile, path: str) -> str:
        """Upload file and return public URL."""

    @abstractmethod
    async def cleanup_files(self, files: list) -> None:
        """Delete files from storage."""

    # TODO: maybe think about moving methods below to apart service or mixin
    async def __mime_type_check(self, file: UploadFile) -> None:
        mime = magic.Magic(mime=True)
        content = await file.read(1024)
        await file.seek(0)
        detected_mime = mime.from_buffer(content)

        if detected_mime not in settings.images.allowed_mime_types:
            raise UnsupportedMediaException()

    async def __size_check(self, file: UploadFile) -> None:
        file_size = 0
        while chunk := await file.read(8192):
            file_size += len(chunk)
            if file_size > settings.images.max_size:
                raise FileTooLargeException()
        await file.seek(0)

    async def __extension_check(self, file: UploadFile) -> None:
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in settings.images.allowed_extensions:
            raise UnsupportedMediaException()

    def __secure_filename(self, filename: str) -> str:
        ext = filename.split(".")[-1]
        return f"{uuid.uuid4().hex}.{ext}"

    async def verify_file(self, file: UploadFile) -> bool:
        await self.__mime_type_check(file)
        await self.__size_check(file)
        await self.__extension_check(file)
        return True

    def get_path(self, file: UploadFile, unique_product_slug: str) -> dict:
        filename = self.__secure_filename(file.filename)
        return os.path.join(settings.images.upload_dir, unique_product_slug, filename)


class LocalFileStorage(AbstractFileStorageService):

    # TODO: check if try/except is needed
    async def upload(self, file: UploadFile, path: str) -> str:
        os.makedirs(os.path.dirname(path), exist_ok=True)

        async with aiofiles.open(path, "wb") as f:
            while chunk := await file.read(8192):
                await f.write(chunk)

    async def cleanup_files(self, files: list) -> None:
        for file in files:
            try:
                remove_file = file if isinstance(file, str) else file.file_path
                await aiofiles.os.remove(remove_file)
            except (FileNotFoundError, PermissionError, OSError) as e:
                logger.error("Failed to create product: %s", e, exc_info=True)


class SupabaseFileStorage(AbstractFileStorageService):

    async def upload(self, file: UploadFile, path: str) -> str:
        try:
            contents = await file.read()
            supabase_client.storage.from_(settings.bucket.name).upload(path, contents)
            return path
        except Exception as e:
            logger.error("Failed to upload images: %s", e, exc_info=True)
            raise FileUploadException()

    async def cleanup_files(self, files: list) -> None:
        for file in files:
            try:
                remove_file = file if isinstance(file, str) else file.file_path
                supabase_client.storage.from_(settings.bucket.name).remove(
                    [remove_file],
                )
            except Exception as e:
                logger.error("Failed to delete images: %s", e, exc_info=True)
                raise FileDeletionException()
