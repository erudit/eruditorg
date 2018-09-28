import pytest

from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.urls import resolve
from django.urls import reverse
from django.test import RequestFactory
from django.views.generic import TemplateView

from erudit.test.factories import CollectionFactory
from erudit.test.factories import JournalFactory

from base.test.factories import get_authenticated_request
from base.test.factories import GroupFactory
from base.test.factories import UserFactory
from core.editor.test.factories import ProductionTeamFactory

from apps.userspace.journal.viewmixins import JournalScopeMixin


def get_request(url='/'):
    request = RequestFactory().get('/')
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()
    request.resolver_match = resolve(url)
    return request


@pytest.mark.django_db
class TestJournalScopeMixin:

    def test_can_use_a_journal_passed_in_the_url(self):
        # Setup
        journal = JournalFactory()

        class MyView(JournalScopeMixin, TemplateView):
            template_name = 'dummy.html'

        url = reverse(
            'userspace:journal:information:update', kwargs={'journal_pk': journal.pk})
        request = get_authenticated_request()
        request.url = url
        journal.members.add(request.user)
        journal.save()

        my_view = MyView.as_view()

        # Run
        response = my_view(request, journal_pk=journal.pk)

        # Check
        assert response.status_code == 200
        assert response.context_data['scope_current_journal'] == journal
        assert list(response.context_data['scope_user_journals']) == [journal, ]

    def test_redirects_to_the_scoped_url_if_the_journal_id_is_not_present_in_the_url(self, settings):
        # Setup
        class MyView(JournalScopeMixin, TemplateView):
            template_name = 'dummy.html'

        url = reverse('userspace:journal:information:update')
        request = get_request(url)
        request.user = UserFactory()
        journal = JournalFactory()
        settings.MANAGED_COLLECTIONS = (journal.collection.code, )
        journal.members.add(request.user)
        my_view = MyView.as_view()

        # Run
        response = my_view(request)

        # Check
        assert response.status_code == 302
        assert response.url == reverse(
            'userspace:journal:information:update', kwargs={'journal_pk': journal.pk}
        )

    def test_returns_a_403_error_if_no_journal_can_be_associated_with_the_current_user(self):
        # Setup
        class MyView(JournalScopeMixin, TemplateView):
            template_name = 'dummy.html'

        user = UserFactory.create()
        journal = JournalFactory.create(collection=CollectionFactory())
        url = reverse(
            'userspace:journal:information:update', kwargs={'journal_pk': journal.pk})
        request = get_request(url)
        request.user = user
        my_view = MyView.as_view()

        # Run & check
        with pytest.raises(PermissionDenied):
            my_view(request, journal_pk=journal.pk)

    def test_can_return_all_the_journals_if_the_user_is_a_member_of_a_production_team(self, settings):
        # Setup

        col1, col2 = CollectionFactory.create_batch(2)
        settings.MANAGED_COLLECTIONS = (col1.code, col2.code)

        class MyView(JournalScopeMixin, TemplateView):
            template_name = 'dummy.html'

        user = UserFactory.create()
        group = GroupFactory.create(name='Production team')
        production_team = ProductionTeamFactory.create(group=group, identifier='main')

        user.groups.add(group)

        journal1 = JournalFactory.create(collection=col1)
        journal2 = JournalFactory.create(collection=col2)

        production_team.journals.add(journal1)
        production_team.journals.add(journal2)
        production_team.save()

        url = reverse(
            'userspace:journal:information:update', kwargs={'journal_pk': journal1.pk})
        request = get_request(url)
        request.user = user
        my_view = MyView()
        my_view.request = request

        # Run & check
        journals = my_view.get_user_journals()
        assert journals
        assert list(journals) == list((journal1, journal2,))
