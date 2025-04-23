from typing import Optional

from fastapi import HTTPException, status
from pydantic import ValidationError

from app.core.exceptions.base import BaseAppException
from app.core.settings import settings


class ItemNotFoundException(BaseAppException):
    """Raised when a database record is not found."""

    def __init__(self, meta: Optional[dict] = None):
        super().__init__(
            error_code="not_found",
            detail="Ресурс не знайдено",
            status_code=status.HTTP_404_NOT_FOUND,
            meta=meta or {},
        )


class ItemAlreadyExistsException(BaseAppException):
    """Raised when a database record already exists."""

    def __init__(self, meta: Optional[dict] = None):
        super().__init__(
            error_code="already_exists",
            detail="Ресурс вже існує",
            status_code=status.HTTP_409_CONFLICT,
            meta=meta or {},
        )


class UniqueConstraintViolationsException(BaseAppException):
    """Raised for database unique constraint violations."""

    def __init__(self, violations: list[dict]):
        """
        :param violations: List of violation details in format
        [{"field": "email", "value": "test@example.com"}]
        """
        super().__init__(
            error_code="unique_conflict",
            detail="Конфлікт унікальних значень",
            status_code=status.HTTP_409_CONFLICT,
            meta={"violations": violations},
        )


class ForeignKeyConstraintViolationException(BaseAppException):
    """Виняток для порушень зовнішніх ключів."""

    def __init__(self, violations: list[dict]):
        super().__init__(
            error_code="foreign_key_violation",
            detail="Посилання на неіснуючий запис",
            status_code=status.HTTP_400_BAD_REQUEST,
            meta={"violations": violations},
        )


# ??
class FieldNotFoundException(BaseAppException):
    """Raised when accessing non-existent model field."""

    def __init__(self, meta: Optional[dict] = None):
        super().__init__(
            error_code="invalid_field",
            detail="Невірний параметр запиту",
            status_code=status.HTTP_400_BAD_REQUEST,
            meta=meta or {},
        )


# ??
class ItemNotDeletedException(BaseAppException):
    """Raised when database record deletion fails."""

    def __init__(self, meta: Optional[dict] = None):
        super().__init__(
            error_code="deletion_failed",
            detail="Не вдалося видалити ресурс",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            meta=meta or {},
        )


class UnsupportedMediaException(BaseAppException):
    """Raised for unsupported file types/extensions."""

    def __init__(self, meta: Optional[dict] = None):
        super().__init__(
            error_code="unsupported_media",
            detail="Непідтримуваний формат файлу",
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            meta={
                "allowed_types": list(settings.images.allowed_mime_types),
                **(meta or {}),
            },
        )


# ??
class VerificationFileException(BaseAppException):
    """Raised during file validation failure."""

    def __init__(self, meta: Optional[dict] = None):
        super().__init__(
            error_code="file_validation_failed",
            detail="Помилка перевірки файлу",
            status_code=status.HTTP_400_BAD_REQUEST,
            meta=meta or {},
        )


class FileTooLargeException(BaseAppException):
    """Raised when file size exceeds limit."""

    def __init__(self):
        super().__init__(
            error_code="file_too_large",
            detail="Перевищено максимальний розмір файлу",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            meta={
                "max_size": f"{settings.images.max_size // (1024**2)} MB",
                "allowed_formats": settings.images.allowed_extensions,
            },
        )


class InvalidCredentialsException(BaseAppException):
    """Raised for invalid authentication credentials."""

    def __init__(self):
        super().__init__(
            error_code="invalid_credentials",
            detail="Невірні облікові дані",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidTokenException(BaseAppException):
    """Raised for invalid or expired JWT tokens."""

    def __init__(self):
        super().__init__(
            error_code="invalid_token",
            detail="Помилка авторизації",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidTokenTypeException(BaseAppException):
    """Raised for incorrect token type usage."""

    def __init__(self):
        super().__init__(
            error_code="invalid_token_type",
            detail="Невірний тип токена",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class UserNotFoundException(BaseAppException):
    """Raised when user is not found in database."""

    def __init__(self, meta: Optional[dict] = None):
        super().__init__(
            error_code="user_not_found",
            detail="Користувача не знайдено",
            status_code=status.HTTP_404_NOT_FOUND,
            meta=meta or {},
        )


class InactiveUserException(BaseAppException):
    """Raised when inactive user attempts access."""

    def __init__(self):
        super().__init__(
            error_code="inactive_user",
            detail="Обліковий запис неактивний",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class UserAdminPermissionException(BaseAppException):
    """Raised for unauthorized admin resource access."""

    def __init__(self):
        super().__init__(
            error_code="admin_required",
            detail="Недостатньо прав доступу",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class UserAlreadyExistsException(BaseAppException):
    """Raised during duplicate user registration."""

    def __init__(self):
        super().__init__(
            error_code="user_exists",
            detail="Такий користувач уже існує",
            status_code=status.HTTP_409_CONFLICT,
        )


class ProductCreationException(BaseAppException):
    """Raised during product creation failure."""

    def __init__(self, meta: Optional[dict] = None):
        super().__init__(
            error_code="product_creation_failed",
            detail="Не вдалося створити продукт",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            meta=meta or {},
        )


class MultipleResultsFound(BaseAppException):
    """Raised when multiple results found instead of one."""

    def __init__(self, meta: Optional[dict] = None):
        super().__init__(
            error_code="multiple_results",
            detail="Знайдено кілька результатів",
            status_code=status.HTTP_400_BAD_REQUEST,
            meta=meta or {},
        )


class RepositoryException(BaseAppException):
    """Raised when repository operation fails."""

    def __init__(self, meta: Optional[dict] = None):
        super().__init__(
            error_code="repository_error",
            detail="Помилка репозиторію",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            meta=meta or {},
        )


class InvalidRequestParametersException(BaseAppException):
    """Raised when missing required request parameters."""

    def __init__(self, required_params: list[str]):
        super().__init__(
            error_code="missing_parameters",
            detail="Необхідно вказати одне з обов'язкових полів",
            status_code=status.HTTP_400_BAD_REQUEST,
            meta={
                "required_parameters": required_params,
                "message_hint": "Вкажіть хоча б один з параметрів",
            },
        )


class CustomPydanticValidationException(HTTPException):

    def __init__(self, error: ValidationError):
        errors = []
        for err in error.errors():
            field = ".".join(str(loc) for loc in err["loc"])
            errors.append({"field": field, "message": err["msg"], "type": err["type"]})
        super().__init__(status_code=422, detail={"errors": errors})


class EmptyCartException(BaseAppException):
    def __init__(self, meta: Optional[dict] = None):
        super().__init__(
            error_code="empty_cart",
            detail="Кошик порожній. Неможливо оформити замовлення.",
            status_code=status.HTTP_409_CONFLICT,
            meta=meta or {},
        )
