import factory

from app.models.users import User
from app.schemas.users import ReadUserSchema, RegisterUserSchema


class AuthUserPayloadFactory(factory.Factory):
    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.Faker("password", length=20)
    confirm_password = factory.SelfAttribute("password")

    class Meta:
        model = RegisterUserSchema


class UserFactory(factory.Factory):
    id = factory.Sequence(lambda n: n + 1)  # noqa
    username = factory.Faker("user_name")
    email = factory.Faker("email")
    phone_number = factory.Faker("numerify", text="0#########")
    hashed_password = factory.LazyFunction(lambda: b"hashed-password")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    patronymic = None
    is_active = True
    is_superuser = False
    is_verified = False
    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")

    class Meta:
        model = User


class ReadUserFactory(factory.Factory):
    id = factory.Sequence(lambda n: n + 1)  # noqa
    username = factory.Faker("user_name")
    email = factory.Faker("email")
    phone_number = factory.Faker("numerify", text="0#########")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    patronymic = None
    is_active = True
    is_superuser = False
    is_verified = False
    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")

    class Meta:
        model = ReadUserSchema
