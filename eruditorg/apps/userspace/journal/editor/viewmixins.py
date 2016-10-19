class IssueSubmissionContextMixin(object):

    def get_context_info(self):
        return {
            'username': self.request.user,
            'journal_code': self.current_journal.code,
            'issue_submission': self.object.pk,
        }
