class IssueSubmissionContextMixin:
    def get_context_info(self):
        return {
            "username": self.request.user.username,
            "journal_code": self.current_journal.code,
            "issue_submission": self.object.pk,
        }
