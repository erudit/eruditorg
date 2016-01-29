import factory


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'auth.User'

    username = factory.Sequence(lambda n: 'username{}'.format(n))
