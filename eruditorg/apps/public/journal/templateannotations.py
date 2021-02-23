from django.urls import reverse
from django.utils.safestring import mark_safe

# Injects a `extra` attribute to target models to supply functions
# for use in templates. Cleaner than templatetags and much cleaner
# than putting this in models.


class IssueAnnotator:
    @classmethod
    def annotate(cls, issue, view):
        if issue is None:
            return None
        issue.extra = cls(issue, view)
        return issue

    def __init__(self, issue, view):
        self.issue = issue
        self.view = view

    def detail_url(self):
        issue = self.issue
        if issue.external_url:
            return issue.external_url
        else:
            return reverse(
                "public:journal:issue_detail",
                args=(issue.journal.code, issue.volume_slug, issue.localidentifier),
            )

    def detail_link_attrs(self):
        result = 'href="{}"'.format(self.detail_url())
        if self.issue.external_url:
            result += ' target="_blank"'
        return mark_safe(result)

    def is_locked(self):
        if self.issue.external_url:
            return False  # external issues are never locked
        return self.issue.embargoed and not self.view.content_access_granted
