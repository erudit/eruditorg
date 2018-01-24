import structlog

from django.urls import reverse
from django.utils.safestring import mark_safe

# Injects a `extra` attribute to target models to supply functions
# for use in templates. Cleaner than templatetags and much cleaner
# than putting this in models.
logger = structlog.get_logger(__name__)


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
                'public:journal:issue_detail',
                args=(issue.journal.code, issue.volume_slug, issue.localidentifier))

    def detail_link_attrs(self):
        result = 'href="{}"'.format(self.detail_url())
        if self.issue.external_url:
            result += ' target="_blank"'
        return mark_safe(result)

    def is_locked(self):
        if self.issue.external_url:
            return False  # external issues are never locked
        return self.issue.embargoed and not self.view.content_access_granted


class ArticleAnnotator:
    @classmethod
    def annotate_articles(cls, articles):
        for article in articles:
            article.helper = cls(article)

    def __init__(self, article):
        self.article = article

    def get_formatted_authors(self):
        if self.article.erudit_object:
            return mark_safe(self.article.erudit_object.get_authors(formatted=True, html=True))
        else:
            # we're pretty sure that the code below is useless but we don't dare replace this
            # with assert article.erudit_object just yet. This is why we have this log below
            # so that if this branch ever executes, we'll know about it in Sentry.
            logger.error("Calling get_formatted_authors() with a non-erudit article.")
            authors = [str(author) for author in self.article.authors.all()]
            if len(authors) > 1:
                return ', '.join(authors[:-1]) + ' et ' + authors[-1]
            elif authors:
                return authors[0]
            else:
                return ''
