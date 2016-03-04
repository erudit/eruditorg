from django.test import TestCase

from erudit.factories import JournalFactory

from core.userspace.factories import UserFactory

from ..forms import ObjectPermissionForm


class ObjectPermissionFormTestCase(TestCase):

    def test_journal_init(self):
        user = UserFactory()
        data = {'user': user}
        form = ObjectPermissionForm(**data)
        self.assertEqual(len(form.fields['journal'].choices), 0)

    def test_journal_filter(self):
        user = UserFactory()
        data = {'user': user}

        journal_in = JournalFactory()
        journal_in.members.add(user)
        journal_in.save()

        journal_not_in = JournalFactory()
        form = ObjectPermissionForm(**data)
        choices = [c[0] for c in form.fields['journal'].choices]
        self.assertTrue(journal_in.id in choices)
        self.assertFalse(journal_not_in.id in choices)

    def test_user_init(self):
        user = UserFactory()
        data = {'user': user}
        form = ObjectPermissionForm(**data)
        self.assertEqual(len(form.fields['user'].choices), 0)

    def test_user_filter(self):
        user = UserFactory()
        data = {'user': user}

        user_in = UserFactory()
        user_not_in = UserFactory()
        journal_in = JournalFactory()
        journal_in.members.add(user)
        journal_in.members.add(user_in)
        journal_in.save()

        journal_not_in = JournalFactory()
        journal_not_in.members.add(user_not_in)
        form = ObjectPermissionForm(**data)
        choices = [c[0] for c in form.fields['user'].choices]
        self.assertTrue(user.id in choices)
        self.assertTrue(user_in.id in choices)
        self.assertFalse(user_not_in.id in choices)

    def test_permission_filter(self):
        user = UserFactory()
        data = {'user': user}
        form = ObjectPermissionForm(**data)
        choices = set([c[0] for c in form.fields['permission'].choices])
        self.assertEqual(choices, set(form.get_permission_filters()))
