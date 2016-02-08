# -*- coding: utf-8 -*-

from django.http import Http404

from erudit.models import Journal


class JournalDetailMixin(object):
    def get_object(self):
        try:
            return Journal.objects.get(code=self.kwargs['code'])
        except Journal.DoesNotExist:
            raise Http404
