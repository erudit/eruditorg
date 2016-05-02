# -*- coding: utf-8 -*-

from .citations import SavedCitationList


class SavedCitationListMiddleware(object):
    """ Middleware that associates a list of saved citations to the current request. """

    def process_request(self, request):
        request.saved_citations = SavedCitationList(request)

    def process_response(self, request, response):
        if hasattr(request, 'saved_citations'):
            request.saved_citations.save()
        return response
