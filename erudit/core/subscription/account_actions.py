# -*- coding utf-8 -*-

from core.account_actions import actions
from core.account_actions.action_base import AccountActionBase
from core.email import Email


class IndividualSubscriptionAction(AccountActionBase):
    name = 'individualsubscription'

    def execute(self, token):
        # TODO
        pass

    def send_notification_email(self, token):
        email = Email(
            [token.email, ],
            html_template='subscription/emails/new_subscription_content.html',
            subject_template='subscription/emails/new_subscription_subject.html',
            extra_context={'token': token})
        email.send()


actions.register(IndividualSubscriptionAction)
