# -*- coding: utf-8 -*-

from django.db.models import Q
from django.http import Http404
from ipware.ip import get_ip
from rules.contrib.views import PermissionRequiredMixin

from core.subscription.models import InstitutionalAccount
from core.subscription.models import InstitutionIPAddressRange
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


class ArticleAccessCheckMixin(PermissionRequiredMixin):
    """
    Defines a way to check whether the current user can browse a
    given Érudit article.
    """
    def get_article(self):
        return self.get_permission_object()

    def has_permission(self):
        article = self.get_article()
        # An article can be browsed if...
        #   1- it is in open access
        #   2- the current user has access to it with its individual account
        #   3- the current IP address is inside on of the IP address ranges allowed
        #      to access to it

        # 1- Is the article in open access?
        if article.open_access:
            return True

        # 2- Is the current user allowed to access the article?
        # TODO: add

        # 3- Is the current IP address allowed to access the article as an institution?
        ip = get_ip(self.request)
        institution_accounts = InstitutionalAccount.objects.filter(
            Q(policy__access_full=True) | Q(policy__access_journal=article.issue.journal))
        institutional_access = institution_accounts.exists() and \
            InstitutionIPAddressRange.objects.filter(
                institutionaccount__in=institution_accounts,
                ip_start__lte=ip, ip_end__gte=ip).exists()
        if institutional_access:
            return True

        return False
