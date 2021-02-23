# -*- coding: utf-8 -*-

import collections
import time
import uuid

from .conf import settings as search_settings


class SavedSearchList(collections.deque):
    """ Stores a list of searches. """

    def __init__(self, request, name="saved-searches", *args, **kwargs):
        super(SavedSearchList, self).__init__(maxlen=search_settings.MAX_SAVED_SEARCHES)
        self.request = request
        self.name = name
        self.extend(request.session.get(self.name, []))

    def save(self):
        """ Saves a list of searches into the user's session. """
        self.request.session[self.name] = list(self)

    def add(self, querystring, results_count=0):
        search = {
            "querystring": querystring,
            "results_count": results_count,
            "timestamp": time.time(),
            "uuid": uuid.uuid4().hex,
        }
        super(SavedSearchList, self).append(search)

    def remove(self, uuid):
        for search in self:
            if search.get("uuid") == uuid:
                super(SavedSearchList, self).remove(search)
                return
        raise ValueError
