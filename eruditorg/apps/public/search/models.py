class BaseExternalDocument(object):
    """ Define documents that are to be returned by the API but are not
    stored in the Django database

    The models are lightweight and only define two fields: ``localidentifier``
    and ``data``.

    :param localidentifier: the unique identifier in the search engine
    :param data:
    """

    def __init__(self, localidentifier, data):
        self.localidentifier = localidentifier
        self.data = data


class ResearchReport(BaseExternalDocument):
    pass


class Book(BaseExternalDocument):
    pass


def get_type_for_corpus(corpus):
    return {
        'Dépot': ResearchReport,
        'Livres': Book,
        'Actes': Book
    }[corpus]
