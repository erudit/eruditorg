from django.urls import reverse
from django.utils.safestring import mark_safe

# Injects a `helper` attribute to target models to supply functions
# for use in templates. Cleaner than templatetags and much cleaner
# than putting this in models.


class IssueHelper:
    @classmethod
    def helperize(cls, issue):
        if issue is None:
            return None
        issue.helper = cls(issue)
        return issue

    def __init__(self, issue):
        self.issue = issue

    def detail_url(self):
        issue = self.issue
        if issue.external_url:
            return issue.external_url
        else:
            return reverse(
                'public:journal:issue_detail',
                args=(issue.journal.code, issue.volume_slug, issue.localidentifier))

    def detail_link_attrs(self):
        result = 'href="{}"'.format(self.detail_url())
        if self.issue.external_url:
            result += ' target="_blank"'
        return mark_safe(result)
