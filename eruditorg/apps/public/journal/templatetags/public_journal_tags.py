from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from erudit.models import Issue, Journal

register = template.Library()


@register.filter
def format_article_html_title(article):
    """Formats the article html title

    Display the html_title if it exists otherwise display "untitled"
    """
    if article.html_title:
        return mark_safe(article.html_title)
    else:
        return _("[Article sans titre]")


@register.filter
def format_article_title(article):
    """Formats the article title

    Display the title if it exists otherwise display "untitled"
    """
    return article.title if article.title else _("[Article sans titre]")


@register.simple_tag
def issue_coverpage_url(issue: Issue) -> str:
    """Return the url of the issue's coverpage

    In the future, this function will use the timestamp of the coverpage's last modified date
    to generate an url that will be permanently cacheable.

    It will use the FEDORA_ASSETS_EXTERNAL_URL configuration. If FEDORA_ASSETS_EXTERNAL_URL
    is defined in the settings, an absolute URL will be returned. If it is not, a relative
    URL will be returned.

    :param issue: the issue for which to return a coverpage url
    :return: the url of the issue coverpage
    """
    issue_coverpage_url = reverse(
        "public:journal:issue_coverpage",
        args=(issue.journal.code, issue.volume_slug, issue.localidentifier),
    )
    return issue_coverpage_url


@register.simple_tag
def journal_logo_url(journal: Journal) -> str:
    """Return the url of the journal's logo

    In the future, this function will use the timestamp of the logo's last modified date
    to generate an url that will be permanently cacheable.

    It will use the FEDORA_ASSETS_EXTERNAL_URL configuration. If FEDORA_ASSETS_EXTERNAL_URL
    is defined in the settings, an absolute URL will be returned. If it is not, a
    relative URL will be returned.

    :param journal: the journal for which to return a journal logo url
    :return: the url of the journal logo
    """
    journal_logo_url = reverse("public:journal:journal_logo", args=(journal.code,))
    return journal_logo_url


@register.filter
def join_author_list(author_list):
    author_list = list(author_list)
    if not author_list:
        return ""
    first_author = author_list.pop(0)
    if not author_list:
        return _("Avec {first_author}".format(first_author=first_author))

    last_author = author_list.pop(len(author_list) - 1)
    if not author_list:
        return _(
            "Avec {first_author} et {last_author}".format(
                first_author=first_author, last_author=last_author
            )
        )

    return _("Avec {first_author}, {contributors} et {last_author}").format(
        first_author=first_author,
        contributors=", ".join(str(author) for author in author_list),
        last_author=last_author,
    )


@register.filter
def get_class(value):
    return value.__class__.__name__
