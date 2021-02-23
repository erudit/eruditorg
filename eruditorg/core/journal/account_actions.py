# -*- coding utf-8 -*-

from account_actions.action_base import AccountActionBase
from account_actions.action_pool import actions
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from core.email import Email


class OrganisationMembershipAction(AccountActionBase):
    name = "organisationmembership"

    landing_page_template_name = "public/account_actions/organisation_membership_landing.html"

    def can_be_consumed(self, token, user):
        return token.can_be_consumed and not self._member_exists(token, user)

    def execute(self, token):
        token.content_object.members.add(token.user)

    def get_extra_context(self, token, user):
        return {
            "member_exists": self._member_exists(token, user),
        }

    def get_consumption_redirect_url(self, token):
        return reverse("public:home")

    def get_consumption_success_message(self, token):
        return _("Vous êtes maintenant membre de cette organisation ({org})").format(
            org=token.content_object.name
        )

    def send_notification_email(self, token):
        email = Email(
            [
                token.email,
            ],
            html_template="emails/organisation/new_member_content.html",
            subject_template="emails/organisation/new_member_subject.html",
            extra_context={"token": token},
            tag="www-organisation-nouveau-membre",
        )
        email.send()

    def _member_exists(self, token, user):
        if user.is_authenticated:
            return token.content_object.members.filter(pk=user.pk).exists()
        else:
            return False


actions.register(OrganisationMembershipAction)
