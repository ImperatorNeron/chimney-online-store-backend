import factory

from app.models.categories import Category


class CategoryFactory(factory.Factory):
    id = factory.Sequence(lambda n: n + 1)  # noqa
    name = factory.Sequence(lambda n: f"Category {n + 1}")
    slug = factory.Sequence(lambda n: f"category-{n + 1}")
    file_path = None
    parent_id = None

    class Meta:
        model = Category
