from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

register = template.Library()


@register.filter
def format_article_html_title(article):
    """ Formats the article html title

    Display the html_title if it exists otherwise display "untitled"
    """
    if article.html_title:
        return mark_safe(article.html_title)
    else:
        return _("[Article sans titre]")


@register.filter
def format_article_title(article):
    """ Formats the article title

    Display the title if it exists otherwise display "untitled"
    """
    return article.title if article.title else _("[Article sans titre]")


@register.filter
def join_author_list(author_list):
    author_list = list(author_list)
    if not author_list:
        return ""
    first_author = author_list.pop(0)
    if not author_list:
        return _('Avec {first_author}'.format(first_author=first_author))

    last_author = author_list.pop(len(author_list) - 1)
    if not author_list:
        return _('Avec {first_author} et {last_author}'.format(
            first_author=first_author, last_author=last_author
        ))

    return _('Avec {first_author}, {contributors} et {last_author}').format(
        first_author=first_author,
        contributors=", ".join(str(author) for author in author_list),
        last_author=last_author
    )
