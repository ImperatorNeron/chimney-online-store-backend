from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, PositiveInt


class BaseUserFields(BaseModel):
    email: Optional[EmailStr] = Field(
        default=None,
        min_length=5,
        max_length=255,
        title="Email address of the user",
    )
    phone_number: Optional[str] = Field(
        default=None,
        min_length=9,
        max_length=19,
        title="Phone Number",
        pattern=r"^\d{9,19}$",
        examples=["0961234567"],
    )
    first_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        title="First Name",
        pattern=r"^[A-Za-zА-Яа-яІіЇїЄєҐґ\-' ]+$",
        examples=["Your First Name"],
    )
    last_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        title="Last Name",
        pattern=r"^[A-Za-zА-Яа-яІіЇїЄєҐґ\-' ]+$",
        examples=["Your Last Name"],
    )
    patronymic: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        title="Patronymic",
        pattern=r"^[A-Za-zА-Яа-яІіЇїЄєҐґ\-' ]+$",
        examples=["Your Patronymic"],
    )

    @field_validator("first_name", "last_name", "patronymic")
    @classmethod
    def validate_name_fields(cls, value):
        if value is None:
            return value
        if value.strip() == "":
            raise ValueError("Name field cannot be empty or whitespace only")
        return value.title()


class UsernameField(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        title="Username",
        pattern=r"^[a-zA-Z0-9_-]+$",
        examples=["User123"],
    )


class PasswordField(BaseModel):
    password: str = Field(
        min_length=4,
        max_length=255,
        title="User's password for registration",
        examples=["YouPass123"],
    )


class HashedPasswordField(BaseModel):
    hashed_password: bytes = Field(title="Hashed user's password")


class BaseUserSchema(UsernameField, BaseUserFields):
    pass


class ReadUserSchema(BaseUserSchema):
    id: PositiveInt  # noqa
    is_active: bool = Field(default=True, title="Indicates if the user is active")
    is_superuser: bool = Field(
        default=False,
        title="Indicates if the user is a superuser",
    )
    is_verified: bool = Field(default=False, title="Indicates if the user is verified")
    created_at: datetime = Field(None, title="Timestamp when the post was created")
    updated_at: datetime = Field(None, title="Timestamp when the post was last updated")


class RegisterUserSchema(BaseUserSchema, PasswordField):

    confirm_password: str = Field(
        min_length=4,
        max_length=255,
        title="User's confirm password for registration",
        examples=["YouPass123"],
    )

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Паролі не співпадають")
        return self


class ReadUserWithPasswordSchema(ReadUserSchema, HashedPasswordField):
    pass


class CreateUserSchema(BaseUserSchema, HashedPasswordField):
    pass


class LoginUserSchema(UsernameField, PasswordField):
    pass


class UpdateUserSchema(BaseUserFields):
    hashed_password: Optional[bytes] = Field(None, title="Hashed user's password")


class UserUpdateWithPasswordSchema(BaseUserFields):
    password: Optional[str] = Field(
        None,
        min_length=4,
        max_length=255,
        title="User's password for registration",
        examples=["YouPass123"],
    )
    confirm_password: Optional[str] = Field(
        None,
        min_length=4,
        max_length=255,
        title="User's confirm password for registration",
        examples=["YouPass123"],
    )

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password or self.confirm_password:
            if not self.password or not self.confirm_password:
                raise ValueError(
                    "Обидва поля 'password' та 'confirm_password' повинні бути заповнені",
                )
            if self.password != self.confirm_password:
                raise ValueError("Паролі не співпадають")
        return self
