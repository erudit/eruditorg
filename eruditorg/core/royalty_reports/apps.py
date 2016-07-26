# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class RoyaltyReportsConfig(AppConfig):
    label = 'royalty_reports'
    name = 'core.royalty_reports'
    verbose_name = _('Rapports de redevances')
