import factory


class BookCollectionFactory(factory.django.DjangoModelFactory):

    name = factory.sequence(lambda n: "BookCollection-{}".format(n))
    slug = factory.sequence(lambda n: "BookCollectionSlug-{}".format(n))

    class Meta:
        model = "book.BookCollection"


class BookFactory(factory.django.DjangoModelFactory):
    title = factory.sequence(lambda n: "Book-{}".format(n))
    slug = factory.sequence(lambda n: "BookCollectionSlug-{}".format(n))
    path = "fixtures/incantation/2018"

    collection = factory.SubFactory(BookCollectionFactory)

    class Meta:
        model = "book.Book"
