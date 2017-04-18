from django import template
from django.utils.translation import ugettext_lazy as _
register = template.Library()


@register.filter(name="person_list")
def person_list(authors):
    """ Format a list of persons in a string enumeration"""
    # Create a copy of the list
    if not authors:
        return ""
    authors = list(authors)
    last_author = authors.pop()
    if len(authors) == 0:
        return last_author
    return "{} {} {}".format(
        ", ".join(authors),
        _("et"),
        last_author
    )
