# -*- coding: utf-8 -*-

from django.http import Http404
from django.views.generic import DetailView

from erudit.models import Journal
from eruditarticle.repository import repo
from eruditarticle.fedora import JournalDigitalObject


class JournalDetailView(DetailView):
    model = Journal
    context_object_name = 'journal'
    template_name = 'journal_detail.html'

    def get_object(self):
        try:
            return Journal.objects.get(code=self.kwargs['code'])
        except Journal.DoesNotExist:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super(JournalDetailView, self).get_context_data(**kwargs)

        # Fetches the journal from the fedora repository
        if self.object.pid:
            f_journal = JournalDigitalObject(repo.api, self.object.pid)
            context['fedora_journal'] = f_journal

        return context
