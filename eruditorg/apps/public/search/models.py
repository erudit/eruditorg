from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from eulfedora.util import RequestFailed
from requests.exceptions import ConnectionError

from erudit import models as erudit_models


# These models below are temporary shims that we implement with the same API as the old serializers
# but we instantiate them on the "other side" of the REST API. We do this to ease the transition.
# otherwise, we would have to change the search result template at the same time as we strip the
# django rest framework.


class Article:
    def __init__(self, localidentifier):
        self.localidentifier = localidentifier
        self.obj = erudit_models.Article.objects.get(localidentifier=localidentifier)

    def __getattr__(self, name):
        return getattr(self.obj, name)

    @property
    def authors(self):
        return self.obj.get_formatted_authors()

    @property
    def type(self):
        if self.obj.type:
            return self.obj.get_type_display()
        return _('Article')

    @property
    def paral_titles(self):
        paral_titles = self.obj.titles.filter(paral=True)
        return list(t.title for t in paral_titles)

    @property
    def paral_subtitles(self):
        paral_subtitles = self.obj.subtitles.filter(paral=True)
        return list(t.title for t in paral_subtitles)

    @property
    def abstract(self):
        return self.obj.abstract

    @property
    def collection(self):
        return self.obj.issue.journal.collection.name

    @property
    def reviewed_works(self):
        if self.obj.fedora_object and self.obj.fedora_object.exists:
            return self.obj.erudit_object.get_reviewed_works()

    @property
    def journal_code(self):
        return self.obj.issue.journal.code

    @property
    def series(self):
        return self.obj.issue.journal.name

    @property
    def journal_type(self):
        if self.obj.issue.journal.type:
            return self.obj.issue.journal.type.get_code_display().lower()
        return ''

    @property
    def publication_date(self):
        return self.obj.issue.abbreviated_volume_title

    @property
    def journal_url(self):
        journal = self.obj.issue.journal
        if journal.external_url:
            return journal.external_url
        return reverse('public:journal:journal_detail', args=(journal.code, ))

    @property
    def issue_url(self):
        issue = self.obj.issue
        if issue.external_url:
            return issue.external_url
        return reverse('public:journal:issue_detail', args=(
            issue.journal.code,
            issue.volume_slug,
            issue.localidentifier,
        ))

    @property
    def issue_localidentifier(self):
        return self.obj.issue.localidentifier

    @property
    def issue_title(self):
        return self.obj.issue.name_with_themes

    @property
    def issue_number(self):
        return self.obj.issue.number_for_display

    @property
    def issue_volume(self):
        return self.obj.issue.volume

    @property
    def issue_published(self):
        return self.obj.issue.publication_period or self.obj.issue.year

    @property
    def issue_volume_slug(self):
        return self.obj.issue.volume_slug

    @property
    def pdf_url(self):
        if self.obj.external_pdf_url:
            # If we have a external_pdf_url, then it's always the proper one to return.
            return self.obj.external_pdf_url
        if self.obj.issue.external_url:
            # special case. if our issue has an external_url, regardless of whether we have a
            # fedora object, we *don't* have a PDF url. See the RECMA situation at #1651
            return None
        try:
            if self.obj.fedora_object:
                return reverse('public:journal:article_raw_pdf', kwargs={
                    'journal_code': self.obj.issue.journal.code,
                    'issue_slug': self.obj.issue.volume_slug,
                    'issue_localid': self.obj.issue.localidentifier,
                    'localid': self.obj.localidentifier,
                })
        except (RequestFailed, ConnectionError):  # pragma: no cover
            if settings.DEBUG:
                return False
            raise

    @property
    def keywords(self):
        return [keyword.name for keyword in self.obj.keywords.all()]


class Thesis:
    def __init__(self, localidentifier):
        self.localidentifier = localidentifier
        self.obj = erudit_models.Thesis.objects.get(localidentifier=localidentifier)

    def __getattr__(self, name):
        return getattr(self.obj, name)

    @property
    def authors(self):
        return str(self.obj.author)

    @property
    def collection(self):
        return self.obj.collection.code

    @property
    def collection_name(self):
        return self.obj.collection.name

    @property
    def publication_date(self):
        return self.obj.publication_year

    @property
    def description(self):
        return self.obj.description

    @property
    def keywords(self):
        return [keyword.name for keyword in self.obj.keywords.all()]
