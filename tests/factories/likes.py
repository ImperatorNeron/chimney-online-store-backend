import factory

from app.models.likes import Like


class LikeFactory(factory.Factory):
    id = factory.Sequence(lambda n: n + 1)  # noqa
    user_id = factory.Sequence(lambda n: n + 1)
    product_id = factory.Sequence(lambda n: n + 100)

    class Meta:
        model = Like
