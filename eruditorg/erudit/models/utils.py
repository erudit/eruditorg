from django.utils.translation import gettext_lazy as _


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
