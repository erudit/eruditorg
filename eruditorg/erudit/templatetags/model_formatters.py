from django import template
from erudit.models import utils

register = template.Library()


@register.filter(name="format_editor")
def format_editor(editor):
    person_name = editor.format_name()
    role = editor.role
    if role:
        if "fr" in role:
            role_name = role["fr"]
        elif "fr" in role:
            role_name = role["en"]
        else:
            return person_name
        return "{} ({})".format(person_name, role_name)
    return person_name


@register.filter(name="person_list")
def person_list(authors):
    """ Format a list of persons in a string enumeration"""
    return utils.person_list(authors)
