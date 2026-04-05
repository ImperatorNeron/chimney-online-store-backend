import factory

from app.models.users import User
from app.schemas.users import ReadUserSchema, ReadUserWithPasswordSchema, RegisterUserSchema


class UserIdentifierFactory(factory.Factory):
    username = factory.Faker("bothify", text="user_##??")
    email = factory.Faker("email")


class CommonFactory(UserIdentifierFactory):
    id = factory.Sequence(lambda n: n + 1)  # noqa
    phone_number = factory.Faker("numerify", text="0#########")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    patronymic = None
    is_active = True
    is_superuser = False
    is_verified = False
    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")


class AuthUserPayloadFactory(UserIdentifierFactory):
    password = factory.Faker("password", length=20)
    confirm_password = factory.SelfAttribute("password")

    class Meta:
        model = RegisterUserSchema


class UserFactory(CommonFactory):
    hashed_password = factory.LazyFunction(lambda: b"hashed-password")

    class Meta:
        model = User


class ReadUserFactory(CommonFactory):

    class Meta:
        model = ReadUserSchema


class ReadUserWithPasswordFactory(CommonFactory):
    hashed_password = factory.LazyFunction(lambda: b"hashed-password")

    class Meta:
        model = ReadUserWithPasswordSchema
