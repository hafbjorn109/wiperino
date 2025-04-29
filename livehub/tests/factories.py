import factory
from playerhub.tests.factories import RunFactory


class PollFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'livehub.Poll'

    run = factory.SubFactory(RunFactory)
    question = factory.Faker('sentence', nb_words=6)
    published = factory.Faker('boolean', chance_of_getting_true=20)


class AnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'livehub.Answer'

    poll = factory.SubFactory(PollFactory)
    answer = factory.Faker('sentence', nb_words=3)
    votes = factory.Faker('pyint', min_value=0, max_value=100)
