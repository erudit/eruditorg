# -*- coding: utf-8 -*-

from core.account_actions.views.generic import AccountActionLandingView \
    as BaseAccountActionLandingView
from core.account_actions.views.generic import AccountActionConsumeView  # noqa


class AccountActionLandingView(BaseAccountActionLandingView):
    # We assume that the 'landing_page_template_name' attribute is defined on all the actions.
    template_name = None
