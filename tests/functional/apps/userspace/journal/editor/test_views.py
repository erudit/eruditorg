import pytest
import os

from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from lxml import etree
from resumable_uploads.models import ResumableFile

from base.test.factories import UserFactory
from base.test.testcases import Client, extract_post_args
from core.editor.test.factories import IssueSubmissionFactory
from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.test.factories import AuthorizationFactory
from core.editor.models import IssueSubmission
from core.editor.test import BaseEditorTestCase
from erudit.test.factories import JournalFactory

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture()
def user_can_edit_journal():
    user = UserFactory()
    journal = JournalFactory(members=[user])
    AuthorizationFactory.create_can_manage_issue_subscriptions(user, journal)
    return user, journal


@pytest.mark.django_db
class TestIssueSubmissionDetailView:
    def test_includes_the_status_tracks_into_the_context(self):
        # Setup
        journal = JournalFactory(members=[UserFactory()])
        issue_submission = IssueSubmissionFactory(
            journal=journal, volume="2", contact=journal.members.first()
        )

        issue_submission.submit()
        issue_submission.refuse()
        issue_submission.save()
        user = UserFactory(is_superuser=True)
        client = Client(logged_user=user)
        url = reverse("userspace:journal:editor:detail", args=(journal.pk, issue_submission.pk))
        # Run
        response = client.get(url)
        # Check
        assert response.status_code == 200
        assert len(response.context["status_tracks"]) == 2
        assert response.context["status_tracks"][0].status == IssueSubmission.SUBMITTED
        assert response.context["status_tracks"][1].status == IssueSubmission.NEEDS_CORRECTIONS


@pytest.mark.django_db
class TestIssueSubmissionView:
    def test_editor_views_are_login_protected(self):
        """ Editor views should all be login protected """

        issue_submission = IssueSubmissionFactory()

        client = Client()
        result = client.get(
            reverse("userspace:journal:editor:add", args=(issue_submission.journal.pk,))
        )
        assert isinstance(result, HttpResponseRedirect)

        result = client.get(
            reverse("userspace:journal:editor:issues", args=(issue_submission.journal.pk,))
        )
        assert isinstance(result, HttpResponseRedirect)

        result = client.get(
            reverse(
                "userspace:journal:editor:update",
                kwargs={"journal_pk": issue_submission.journal.pk, "pk": issue_submission.pk},
            )
        )
        assert isinstance(result, HttpResponseRedirect)

    def test_user_filtered_issuesubmissions(self):
        """A user should only be able to see the editor's submissions
        related to his journal's membership.
        """

        issue_submission = IssueSubmissionFactory()

        client = Client(logged_user=UserFactory())

        response = client.get(
            reverse(
                "userspace:journal:editor:update",
                kwargs={"journal_pk": issue_submission.journal.pk, "pk": issue_submission.pk},
            )
        )

        assert response.status_code == 403

    def test_can_submit_changes_to_issue(self):
        """Submitting changes to an issue doesn't crash.

        Previously, we would crash due to a bad reverse match.
        """
        user = UserFactory()
        issue_submission = IssueSubmissionFactory(journal__members=[user])
        AuthorizationFactory.create_can_manage_issue_subscriptions(user, issue_submission.journal)
        client = Client(logged_user=user)
        url = reverse(
            "userspace:journal:editor:update",
            kwargs={"journal_pk": issue_submission.journal.pk, "pk": issue_submission.pk},
        )

        response = client.get(url)
        root = etree.HTML(response.content)
        args = extract_post_args(root)
        # The issue in our DB doesn't have a year or number, but they are required, so here we go.
        args["year"] = "2016"
        args["number"] = "01"
        response = client.post(url, data=args)
        assert response.status_code == 302
        assert response.url == reverse(
            "userspace:journal:editor:detail",
            kwargs={"journal_pk": issue_submission.journal.pk, "pk": issue_submission.pk},
        )

    def test_logged_add_journalsubmission(self):
        """ Logged users should be able to see journal submissions """
        user = UserFactory()
        journal = JournalFactory(members=[user])
        AuthorizationFactory.create_can_manage_issue_subscriptions(user, journal)
        client = Client(logged_user=user)

        result = client.get(
            reverse("userspace:journal:editor:add", kwargs={"journal_pk": journal.pk})
        )
        assert isinstance(result, TemplateResponse)

    def test_cannot_upload_while_adding(self):
        """Test upload widget absence in creation

        We need to save it before the IssueSubmission before
        uploading so that file chunks are associated with the issue
        submission."""
        user = UserFactory()
        journal = JournalFactory(members=[user])
        AuthorizationFactory.create_can_manage_issue_subscriptions(user, journal)

        client = Client(logged_user=user)
        response = client.get(
            reverse("userspace:journal:editor:add", kwargs={"journal_pk": journal.pk})
        )
        root = etree.HTML(response.content)
        assert len(root.cssselect("#id_submissions")) == 0

    def test_can_create_issuesubmission(self, user_can_edit_journal):
        """Test that we can create an issue submission"""
        user, journal = user_can_edit_journal
        issue_submission_count = IssueSubmission.objects.count()

        data = {
            "journal": journal.pk,
            "year": "2015",
            "volume": "2",
            "number": "2",
            "contact": user.pk,
            "comment": "lorem ipsum dolor sit amet",
        }

        client = Client(logged_user=user)

        client.post(reverse("userspace:journal:editor:add", args=(journal.pk,)), data)

        assert IssueSubmission.objects.count() == issue_submission_count + 1

    def test_can_upload_while_updating(self, user_can_edit_journal):
        """Test upload widget presence in update

        The file upload widget should be present on update forms.
        Files are uploaded to an existing IssueSubmission so
        progress can be tracked.
        """
        user, journal = user_can_edit_journal
        client = Client(logged_user=user)

        issue_submission = IssueSubmissionFactory(journal=journal)

        response = client.get(
            reverse(
                "userspace:journal:editor:update",
                kwargs={"journal_pk": journal.pk, "pk": issue_submission.pk},
            )
        )

        root = etree.HTML(response.content)

        assert len(root.cssselect("#id_submissions")) > 0

    def test_can_update_an_issue_submission_even_if_it_is_submitted(self, user_can_edit_journal):
        # Setup
        user, journal = user_can_edit_journal
        issue_submission = IssueSubmissionFactory(journal=journal)
        issue_submission.submit()
        issue_submission.save()
        client = Client(logged_user=user)
        url = reverse(
            "userspace:journal:editor:update",
            kwargs={"journal_pk": journal.pk, "pk": issue_submission.pk},
        )
        # Run
        response = client.get(url)
        # Check
        assert response.status_code == 200


class TestIssueSubmissionAttachmentView(BaseEditorTestCase):
    def test_cannot_be_browsed_by_users_who_cannot_download_submission_files(self):
        # Setup
        with open(os.path.join(FIXTURE_ROOT, "pixel.png"), mode="rb") as f:
            rfile = ResumableFile.objects.create(
                path=os.path.join(FIXTURE_ROOT, "pixel.png"), filesize=f.tell(), uploadsize=f.tell()
            )

        user = UserFactory()
        client = Client(logged_user=user)
        self.issue_submission.last_files_version.submissions.add(rfile)
        url = reverse("userspace:journal:editor:attachment_detail", kwargs={"pk": rfile.pk})
        # Run
        response = client.get(url, follow=False)
        # Check
        assert response.status_code == 403

    def test_can_be_browsed_by_users_who_can_manage_issue_submissions(self):
        with open(os.path.join(FIXTURE_ROOT, "pixel.png"), mode="rb") as f:
            rfile = ResumableFile.objects.create(
                path=os.path.join(FIXTURE_ROOT, "pixel.png"), filesize=f.tell(), uploadsize=f.tell()
            )

        user = UserFactory()
        self.journal.members.add(user)
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal),
            object_id=self.journal.id,
            user=user,
            authorization_codename=AC.can_manage_issuesubmission.codename,
        )

        client = Client(logged_user=user)
        self.issue_submission.last_files_version.submissions.add(rfile)
        url = reverse(
            "userspace:journal:editor:attachment_detail",
            kwargs={"journal_pk": self.journal.pk, "pk": rfile.pk},
        )
        response = client.get(url)
        # we're redirected to the attachment path in the media folder
        assert response.status_code == 302

    def test_can_be_browsed_by_users_who_can_review_issue_submissions(self):
        with open(os.path.join(FIXTURE_ROOT, "pixel.png"), mode="rb") as f:
            rfile = ResumableFile.objects.create(
                path=os.path.join(FIXTURE_ROOT, "pixel.png"), filesize=f.tell(), uploadsize=f.tell()
            )

        user = UserFactory()
        AuthorizationFactory.create(
            user=user, authorization_codename=AC.can_review_issuesubmission.codename
        )
        self.journal.members.add(user)

        client = Client(logged_user=user)
        self.issue_submission.last_files_version.submissions.add(rfile)
        url = reverse(
            "userspace:journal:editor:attachment_detail",
            kwargs={"journal_pk": self.journal.pk, "pk": rfile.pk},
        )
        response = client.get(url)
        assert response.status_code == 302

    def test_filename_special_characters_are_urlencoded(self):
        with open(os.path.join(FIXTURE_ROOT, "pixel#.png"), mode="rb") as f:
            rfile = ResumableFile.objects.create(
                path=os.path.join(FIXTURE_ROOT, "pixel#.png"),
                filesize=f.tell(),
                uploadsize=f.tell(),
            )

        user = UserFactory()
        AuthorizationFactory.create(
            user=user, authorization_codename=AC.can_review_issuesubmission.codename
        )
        self.journal.members.add(user)

        client = Client(logged_user=user)
        self.issue_submission.last_files_version.submissions.add(rfile)
        url = reverse(
            "userspace:journal:editor:attachment_detail",
            kwargs={"journal_pk": self.journal.pk, "pk": rfile.pk},
        )
        response = client.get(url)
        assert "pixel%23" in response.url

    def test_filename_spaces_are_not_urlencoded(self):
        with open(os.path.join(FIXTURE_ROOT, "pixel, .png"), mode="rb") as f:
            rfile = ResumableFile.objects.create(
                path=os.path.join(FIXTURE_ROOT, "pixel, .png"),
                filesize=f.tell(),
                uploadsize=f.tell(),
            )

        user = UserFactory()
        AuthorizationFactory.create(
            user=user, authorization_codename=AC.can_review_issuesubmission.codename
        )
        self.journal.members.add(user)

        client = Client(logged_user=user)
        self.issue_submission.last_files_version.submissions.add(rfile)
        url = reverse(
            "userspace:journal:editor:attachment_detail",
            kwargs={"journal_pk": self.journal.pk, "pk": rfile.pk},
        )
        response = client.get(url)
        assert "pixel%2C%20" in response.url


class TestIssueSubmissionApproveView(BaseEditorTestCase):
    def test_cannot_be_browsed_by_a_user_who_cannot_review_issue_submissions(self):
        # Setup
        user = UserFactory()
        self.journal.members.add(user)
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal),
            object_id=self.journal.id,
            user=user,
            authorization_codename=AC.can_manage_issuesubmission.codename,
        )

        client = Client(logged_user=user)
        url = reverse(
            "userspace:journal:editor:transition_approve",
            args=(
                self.journal.pk,
                self.issue_submission.pk,
            ),
        )

        # Run
        response = client.post(url)

        # Check
        assert response.status_code == 403

    def test_can_approve_an_issue_submission(self):
        # Setup
        user = UserFactory(is_superuser=True)

        client = Client(logged_user=user)
        url = reverse(
            "userspace:journal:editor:transition_approve",
            args=(
                self.journal.pk,
                self.issue_submission.pk,
            ),
        )

        self.issue_submission.submit()
        self.issue_submission.save()

        # Run
        response = client.post(url)

        # Check
        assert response.status_code == 302
        self.issue_submission.refresh_from_db()
        assert self.issue_submission.status == IssueSubmission.VALID

    def test_sends_a_notification_email(self):
        # Setup
        u = UserFactory(is_superuser=True)

        client = Client(logged_user=u)
        url = reverse(
            "userspace:journal:editor:transition_approve",
            args=(
                self.journal.pk,
                self.issue_submission.pk,
            ),
        )

        self.issue_submission.contact = u
        self.issue_submission.submit()
        self.issue_submission.save()

        # Run
        response = client.post(url)

        # Check
        assert response.status_code == 302
        self.issue_submission.refresh_from_db()
        assert self.issue_submission.status == IssueSubmission.VALID
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to[0] == u.email


class TestIssueSubmissionRefuseView(BaseEditorTestCase):
    def test_cannot_be_browsed_by_a_user_who_cannot_review_issue_submissions(self):
        # Setup
        user = UserFactory()
        self.journal.members.add(user)
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal),
            object_id=self.journal.id,
            user=user,
            authorization_codename=AC.can_manage_issuesubmission.codename,
        )

        client = Client(logged_user=user)
        url = reverse(
            "userspace:journal:editor:transition_refuse",
            args=(
                self.journal.pk,
                self.issue_submission.pk,
            ),
        )

        # Run
        response = client.post(url)

        # Check
        assert response.status_code == 403

    def test_can_refuse_an_issue_submission(self):
        # Setup
        user = UserFactory(is_superuser=True)

        client = Client(logged_user=user)
        url = reverse(
            "userspace:journal:editor:transition_refuse",
            args=(
                self.journal.pk,
                self.issue_submission.pk,
            ),
        )

        self.issue_submission.submit()
        self.issue_submission.save()

        # Run
        response = client.post(url)

        # Check
        assert response.status_code == 302
        assert self.issue_submission.files_versions.count() == 2

    def test_can_refuse_an_issue_submission_with_a_comment(self):
        # Setup
        user = UserFactory(is_superuser=True)

        client = Client(logged_user=user)
        url = reverse(
            "userspace:journal:editor:transition_refuse",
            args=(
                self.journal.pk,
                self.issue_submission.pk,
            ),
        )

        self.issue_submission.submit()
        self.issue_submission.save()

        # Run
        response = client.post(url, {"comment": "This is a comment!"})

        # Check
        assert response.status_code == 302
        assert self.issue_submission.files_versions.count() == 2
        track = self.issue_submission.last_status_track
        assert track.comment == "This is a comment!"

    def test_sends_a_notification_email(self):
        # Setup
        u = UserFactory(is_superuser=True)

        client = Client(logged_user=u)
        url = reverse(
            "userspace:journal:editor:transition_refuse",
            args=(
                self.journal.pk,
                self.issue_submission.pk,
            ),
        )

        self.issue_submission.contact = u
        self.issue_submission.submit()
        self.issue_submission.save()

        # Run
        response = client.post(url)

        # Check
        assert response.status_code == 302
        self.issue_submission.refresh_from_db()
        assert self.issue_submission.status == IssueSubmission.NEEDS_CORRECTIONS
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to[0] == u.email


class TestIssueSubmissionDeleteView(BaseEditorTestCase):
    def test_cannot_be_browsed_by_a_user_who_cannot_manage_issue_submissions(self):
        # Setup
        user = UserFactory()

        client = Client(logged_user=user)
        url = reverse(
            "userspace:journal:editor:delete",
            args=(
                self.journal.pk,
                self.issue_submission.pk,
            ),
        )

        # Run
        response = client.post(url)

        # Check
        assert response.status_code == 403

    def test_can_delete_an_issue_submission(self):
        # Setup
        user = UserFactory(is_superuser=True)

        client = Client(logged_user=user)
        url = reverse(
            "userspace:journal:editor:delete",
            args=(
                self.journal.pk,
                self.issue_submission.pk,
            ),
        )
        deleted_pk = self.issue_submission.pk

        # Run
        response = client.post(url)

        # Check
        assert response.status_code == 302
        assert deleted_pk not in IssueSubmission.objects.values_list("pk", flat=True)
