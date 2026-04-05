from datetime import datetime, timezone

import factory
from factory import Faker

from app.models.messages import Message


class MessageFactory(factory.Factory):
    id = factory.Sequence(lambda n: n + 1)  # noqa
    user_name = Faker("first_name")
    phone_number = Faker("numerify", text="0#########")
    message = Faker("sentence", nb_words=10)
    status = "new"
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

    class Meta:
        model = Message
