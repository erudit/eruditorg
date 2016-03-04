from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied

from .models import IndividualAccount


class LegacyBackend(ModelBackend):
    """ Authenticate users against IndividualAccount with sha1 custom
    encryption from old system.
    """

    def authenticate(self, username=None, password=None):

        try:
            account = IndividualAccount.objects.get(username=username)
        except IndividualAccount.DoesNotExist:
            raise PermissionDenied()

        if account.sha1(password) == account.password:
            return account
