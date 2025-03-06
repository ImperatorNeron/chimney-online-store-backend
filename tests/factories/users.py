import factory

from app.schemas.users import RegisterUserSchema


class AuthUserPayloadFactory(factory.Factory):
    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.Faker("password", length=20)

    class Meta:
        model = RegisterUserSchema
