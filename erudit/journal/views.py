# -*- coding: utf-8 -*-

from django.http import Http404
from django.views.generic import DetailView

from erudit.models import Journal


class JournalDetailView(DetailView):
    model = Journal
    context_object_name = 'journal'
    template_name = 'journal_detail.html'

    def get_object(self):
        try:
            return Journal.objects.get(code=self.kwargs['code'])
        except Journal.DoesNotExist:
            raise Http404
