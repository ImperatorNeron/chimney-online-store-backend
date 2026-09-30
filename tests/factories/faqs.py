import factory
from factory import Faker

from app.models.faq import FAQ


class FAQFactory(factory.Factory):
    id = factory.Sequence(lambda n: n)  # noqa
    question = Faker("sentence", nb_words=6)
    answer = Faker("paragraph", nb_sentences=3)
    youtube_url = Faker("url")

    class Meta:
        model = FAQ
