import factory
from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Faker('user_name', locale='pl_PL')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'pass1234')
