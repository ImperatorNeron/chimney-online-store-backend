from fastapi import status

from app.core.exceptions.base import BaseAppException
from app.models.base import BaseModel


class ItemNotFoundException(BaseAppException):
    """Raised when a database record is not found."""

    def __init__(self, model: BaseModel, item_id: int):
        model_name = model.__name__
        super().__init__(
            detail=f"{model_name} з id {item_id} не знайдено",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UniqueConstraintViolationsException(BaseAppException):
    """Raised for database unique constraint violations."""

    def __init__(self, violations: list):
        super().__init__(
            detail=violations,
            status_code=status.HTTP_409_CONFLICT,
        )


class FieldNotFoundException(BaseAppException):
    """Raised when accessing non-existent model field."""

    def __init__(self, field_name: str, model_name: str):
        super().__init__(
            detail=f"Поле '{field_name}' не існує в моделі '{model_name}'.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class ItemNotDeletedException(BaseAppException):
    """Raised when database record deletion fails."""

    def __init__(self, item_id: int, model_name: str):
        super().__init__(
            detail=f"Елемент з ID '{item_id}' не був видалений у моделі '{model_name}'.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class UnsupportedMediaException(BaseAppException):
    """Raised for unsupported file types/extensions."""

    def __init__(self, media_type: str | None = None, extension: str | None = None):
        detail = "Непідтримуваний файл"
        if media_type:
            detail += f": тип {media_type}"
        if extension:
            detail += f": розширення {extension}"
        super().__init__(
            detail=detail,
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )


class VerificationFileException(BaseAppException):
    """Raised during file validation failure."""

    def __init__(self):
        super().__init__(
            detail="Помилка перевірки файлу",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class FileTooLargeException(BaseAppException):
    """Raised during file size too big."""

    def __init__(self):
        super().__init__(
            detail="Файл занадто великий",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        )


class InvalidCredentialsException(BaseAppException):
    """Raised for invalid authentication credentials."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірні облікові дані",
        )


class InvalidTokenException(BaseAppException):
    """Raised for invalid or expired JWT tokens."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний токен",
        )


class InvalidTokenTypeException(BaseAppException):
    """Raised for incorrect token type usage."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний тип токена",
        )


class UserNotFoundException(BaseAppException):
    """Raised when user is not found in database."""

    def __init__(self, detail="Користувача не знайдено"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class InactiveUserException(BaseAppException):
    """Raised when inactive user attempts access."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Користувач неактивний",
        )


class UserAdminPermissionException(BaseAppException):
    """Raised for unauthorized admin resource access."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас немає доступу до вмісту",
        )


class UserAlreadyExistsException(BaseAppException):
    """Raised during duplicate user registration."""

    def __init__(self, detail="Користувач вже існує"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class ProductCreationError(BaseAppException):
    """Raised during product creation."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка створення продукту",
        )
