# -*- coding: utf-8 -*-

from django.views.generic import TemplateView

from erudit.models import Issue


class HomeView(TemplateView):
    """
    This is the main view of the Érudit's public site.
    """
    template_name = 'public/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        # Includes the latest issues
        context['latest_issues'] = Issue.objects.filter(date_published__isnull=False) \
            .select_related('journal').order_by('-date_published')[:6]

        return context
