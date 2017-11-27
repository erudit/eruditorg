# -*- coding: utf-8 -*-

from django.views.generic import ListView

from base.viewmixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin
from core.royalty_reports.models import JournalRoyalty

from ..viewmixins import JournalScopeMixin


class JournalRoyaltyListView(
        LoginRequiredMixin, JournalScopeMixin, MenuItemMixin, ListView):
    context_object_name = 'reports'
    menu_journal = 'royalty_reports'
    model = JournalRoyalty
    template_name = 'userspace/journal/royalty_reports/list.html'

    def get_queryset(self):
        qs = super(JournalRoyaltyListView, self).get_queryset()
        return qs.select_related('royalty_report', 'journal') \
            .filter(journal_id=self.current_journal.id, royalty_report__published=True) \
            .order_by('-royalty_report__end')
