import factory
from factory import fuzzy
from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Faker('user_name', locale='pl_PL')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'pass1234')


class RunFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'playerhub.Run'

    name = factory.Faker('word')
    game = factory.Faker('sentence', nb_words=2)
    mode = fuzzy.FuzzyChoice(['SPEEDRUN', 'WIPECOUNTER'])
    user = factory.SubFactory(UserFactory)
    is_finished = factory.Faker('boolean', chance_of_getting_true=20)
    session_code = factory.Faker('bothify', text='???-####')


class WipeCounterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'playerhub.WipeCounter'

    run = factory.SubFactory(RunFactory)
    segment_name = factory.Faker('word')
    count = factory.Faker('pyint', min_value=0, max_value=100)
    is_finished = factory.Faker('boolean', chance_of_getting_true=20)


class TimerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'playerhub.Timer'

    run = factory.SubFactory(RunFactory)
    segment_name = factory.Faker('word')
    elapsed_time = factory.Faker('pyfloat', positive=True, right_digits=2, min_value=0, max_value=9999)
    is_finished = factory.Faker('boolean', chance_of_getting_true=20)


