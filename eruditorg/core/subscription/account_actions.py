# -*- coding utf-8 -*-

from account_actions.action_base import AccountActionBase
from account_actions.action_pool import actions
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from core.email import Email

from .models import JournalAccessSubscription


class IndividualSubscriptionAction(AccountActionBase):
    name = 'individualsubscription'

    landing_page_template_name = 'public/account_actions/individual_subscription_landing.html'

    def can_be_consumed(self, token, user):
        return token.can_be_consumed and not self._subscription_exists(token, user)

    def execute(self, token):
        subscription = JournalAccessSubscription.objects.create(
            user=token.user,
            journal_management_subscription=token.content_object,
        )

        subscription.journals.add(token.content_object.journal)
        subscription.save()

    def get_extra_context(self, token, user):
        return {
            'subscription_exists': self._subscription_exists(token, user),
        }

    def get_consumption_redirect_url(self, token):
        return reverse(
            'public:journal:journal_detail',
            kwargs={'code': token.content_object.journal.code})

    def get_consumption_success_message(self, token):
        return _('Votre abonnement a bien été pris en compte')

    def send_notification_email(self, token):
        email = Email(
            [token.email, ],
            html_template='emails/subscription/journal/new_subscription_content.html',
            subject_template='emails/subscription/journal/new_subscription_subject.html',
            extra_context={'token': token})
        email.send()

    def _subscription_exists(self, token, user):
        if user.is_authenticated:
            # Computes a boolean indicating if a subscription already exists for the current user.
            return JournalAccessSubscription.objects.filter(
                user_id=user.id, journal_management_subscription=token.object_id).exists()
        else:
            return False


actions.register(IndividualSubscriptionAction)
