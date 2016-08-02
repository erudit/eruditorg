# -*- coding: utf-8 -*-

from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver


@receiver(user_logged_out)
def empty_authenticated_user_saved_citation_list(sender, request, user, **kwargs):
    if user and hasattr(request, 'saved_citations'):
        # We want to prevent the saved citations list associated to the current user from being
        # saved when the users logs out. So we manually "remove" the saved citations list from the
        # request object in order to prevent it to be associated with the next request.
        delattr(request, 'saved_citations')
