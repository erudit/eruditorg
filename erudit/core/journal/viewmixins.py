# -*- coding: utf-8 -*-

from django.http import Http404
from django.utils.functional import cached_property

from erudit.models import Journal


class JournalCodeDetailMixin(object):
    """
    Simply allows retrieving a Journal instance using its code.
    """
    def get_journal(self):
        try:
            return Journal.objects.get(code=self.kwargs['code'])
        except Journal.DoesNotExist:
            raise Http404

    def get_object(self, queryset=None):
        return self.get_journal()

    @cached_property
    def journal(self):
        return self.get_journal()
