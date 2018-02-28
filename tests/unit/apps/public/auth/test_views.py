import pytest
import mock
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory
from base.test.factories import UserFactory
from base.test.factories import get_authenticated_request
from erudit.test.factories import JournalFactory
from core.authorization.test.factories import AuthorizationFactory
from core.authorization.defaults import AuthorizationConfig as AC
from apps.public.auth.views import UserLoginLandingRedirectView


@pytest.fixture()
def test_view(monkeypatch):
    monkeypatch.setattr('apps.public.auth.views.messages', mock.Mock())
    return UserLoginLandingRedirectView()


@pytest.mark.django_db
class TestUserLoginLandingRedirectView:

    def test_login_redirects_superuser_to_dashboard(self, test_view):
        superuser = UserFactory(is_superuser=True)
        request = get_authenticated_request(user=superuser)
        test_view.request = request
        assert test_view.get_redirect_url() == reverse('userspace:dashboard')

    def test_login_redirects_individual_subscriber_to_next_if_next_is_specified(self, test_view):
        normal_user = UserFactory()
        request = RequestFactory().get('/', data={"next": "/fr/revues/"})
        request.user = normal_user
        test_view.request = request
        assert test_view.get_redirect_url() == '/fr/revues/'

    def test_login_redirects_individual_subscriber_to_homepage_if_no_referer(self, test_view):
        normal_user = UserFactory()
        request = get_authenticated_request(user=normal_user)
        test_view.request = request
        assert test_view.get_redirect_url() == reverse('public:home')

    def test_login_redirects_journal_member_to_dashboard(self, test_view):
        normal_user = UserFactory()
        request = get_authenticated_request(user=normal_user)
        journal = JournalFactory()
        journal.members.add(normal_user)
        journal.save()
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(journal), object_id=journal.id,
            user=normal_user, authorization_codename=AC.can_edit_journal_information.codename)
        test_view.request = request
        assert test_view.get_redirect_url() == reverse('userspace:dashboard')

    def test_login_redirects_organisation_member_to_dashboard(self, test_view):
        pass
