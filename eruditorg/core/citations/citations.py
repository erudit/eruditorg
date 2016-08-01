# -*- coding: utf-8 -*-

from erudit.models import EruditDocument

from .models import SavedCitationList as DBSavedCitationList


class SavedCitationList(set):
    """ Stores a set of Érudit document citations. """

    def __init__(self, request, name='saved-citations', *args, **kwargs):
        super(SavedCitationList, self).__init__(*args, **kwargs)
        self.request = request
        self.name = name

        if hasattr(self.request, 'user') and self.request.user.is_authenticated():
            # If the user is authenticated we want saved citations list items to be retrieved from
            # the database and not from the session.
            db_clist, _ = DBSavedCitationList.objects.get_or_create(user=self.request.user)
            document_ids = db_clist.documents.values_list('id', flat=True)
            document_ids = list(map(str, document_ids))
        else:
            # Otherwise the documents IDs are retrieved in the user's session.
            document_ids = request.session.get(self.name, [])

        self.update(document_ids)

    def __contains__(self, document):
        document_id = str(document.id) if isinstance(document, EruditDocument) else str(document)
        return super(SavedCitationList, self).__contains__(document_id)

    def save(self):
        """ Saves a list of citations into the user's session. """
        self.request.session[self.name] = list(self)
        # If the user is authenticated the list of articles should be associated to the User
        # instance by creating or updating a SavedCitationList instance.
        if self.request.user.is_authenticated() and len(self):
            db_clist, _ = DBSavedCitationList.objects.get_or_create(user=self.request.user)
            db_clist.documents.add(*EruditDocument.objects.filter(id__in=list(self)))

    def add(self, document):
        document_id = str(document.id) if isinstance(document, EruditDocument) else str(document)
        super(SavedCitationList, self).add(document_id)

    def remove(self, document):
        document_id = str(document.id) if isinstance(document, EruditDocument) else str(document)
        super(SavedCitationList, self).remove(document_id)
