from erudit.models import Article
from erudit.solr.models import SolrDocument
from .models import SavedCitation


class SavedCitationList(set):
    """ Stores a set of Érudit document citations. """

    def __init__(self, request, name='saved-citations', *args, **kwargs):
        super(SavedCitationList, self).__init__(*args, **kwargs)
        self.request = request
        self.name = name

        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            # If the user is authenticated we want saved citations list items to be retrieved from
            # the database and not from the session.
            solr_ids = self.request.user.saved_citations.values_list('solr_id', flat=True)
        else:
            # Otherwise the documents IDs are retrieved in the user's session.
            solr_ids = request.session.get(self.name, [])
        self.update(solr_ids)

    @staticmethod
    def _coerce(elem):
        if isinstance(elem, Article):
            return elem.solr_id
        elif isinstance(elem, SolrDocument):
            return elem.localidentifier
        elif isinstance(elem, str):
            return elem
        else:
            ValueError()

    def __contains__(self, elem):
        return super().__contains__(self._coerce(elem))

    def save(self):
        """ Saves a list of citations into the user's session or in the database. """
        # If the user is authenticated the list of articles should be associated to the User
        # instance by creating or updating a SavedCitationList instance.
        if self.request.user.is_authenticated:
            self.request.user.saved_citations.all().delete()
            to_create = [SavedCitation(user=self.request.user, solr_id=x) for x in self]
            self.request.user.saved_citations.bulk_create(to_create)
        else:
            self.request.session[self.name] = list(self)

    def add(self, elem):
        super().add(self._coerce(elem))

    def remove(self, elem):
        super().remove(self._coerce(elem))
