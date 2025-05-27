import logging
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

import aiofiles
import magic
from fastapi import UploadFile

from app.core.exceptions.common import FileTooLargeException, UnsupportedMediaException
from app.core.settings import settings


logger = logging.getLogger(__name__)


class AbstractFileUploadService(ABC):

    @abstractmethod
    async def verify_file(self, file: UploadFile) -> bool:
        pass

    @abstractmethod
    async def cleanup_files(self, files: list) -> None:
        pass

    @abstractmethod
    def get_metadata(self, file: UploadFile) -> dict:
        pass

    @abstractmethod
    async def bwrite_file(self, file: UploadFile, path: str) -> None:
        pass


class FileUploadService(AbstractFileUploadService):

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

    async def cleanup_files(self, files: list) -> None:
        for file in files:
            try:
                await aiofiles.os.remove(file.file_path)
            except (FileNotFoundError, PermissionError, OSError) as e:
                logger.error("Failed to create product: %s", e, exc_info=True)

    def get_metadata(self, file: UploadFile) -> dict:
        filename = self.__secure_filename(file.filename)
        filepath = settings.images.upload_dir / filename
        return {
            "name": str(filename),
            "path": str(filepath),
        }

    async def bwrite_file(self, file: UploadFile, path: str) -> None:
        async with aiofiles.open(path, "wb") as f:
            while chunk := await file.read(8192):
                await f.write(chunk)
