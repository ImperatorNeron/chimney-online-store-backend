from fastapi import status

from app.core.exceptions.base import BaseAppException
from app.models.base import BaseModel


class ItemNotFoundException(BaseAppException):

    def __init__(self, model: BaseModel, item_id: int):
        model_name = model.__name__
        super().__init__(
            detail=f"{model_name} with id {item_id} not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UniqueConstraintViolationsException(BaseAppException):

    def __init__(self, violations: list):
        super().__init__(
            detail=violations,
            status_code=status.HTTP_409_CONFLICT,
        )


class FieldNotFoundException(BaseAppException):
    """Custom exception for handling non-existent fields in the model."""

    def __init__(self, field_name: str, model_name: str):
        super().__init__(
            detail=f"Field '{field_name}' does not exist in the model '{model_name}'.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class ItemNotDeletedException(BaseAppException):
    def __init__(self, item_id: int, model_name: str):
        super().__init__(
            detail=f"Item with ID '{item_id}' wasn`t deleted in the model '{model_name}'.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class UnsupportedMediaTypeException(BaseAppException):
    def __init__(self, media_type: str):
        super().__init__(
            detail=f"Invalid file type: {media_type}",
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )


class UnsupportedMediaExtensionException(BaseAppException):
    def __init__(self, media_extension: str):
        super().__init__(
            detail=f"Invalid file extension: {media_extension}",
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )


class VerificationFileException(BaseAppException):
    def __init__(self):
        super().__init__(
            detail="Error validating file",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
