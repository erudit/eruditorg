from django import template
from erudit.models import utils

register = template.Library()


@register.filter(name="format_person")
def format_person(person):
        formatted_person_name = ""
        keys_order = ['prefix', 'firstname', 'othername', 'lastname', 'suffix']
        first_item = True
        for index, key in enumerate(keys_order):
            if key in person and person[key]:
                if first_item:
                    value = ""
                    first_item = False
                else:
                    value = " "
                formatted_person_name += value + person[key]
        if 'pseudo' in person:
            return formatted_person_name + ', alias ' + format_person(person['pseudo'])
        return formatted_person_name


@register.filter(name="format_editor")
def format_editor(editor):
    person_name = format_person(editor)
    role = editor['role']
    if role:
        if 'fr' in role:
            role_name = role['fr']
        elif 'fr' in role:
            role_name = role['en']
        else:
            return person_name
        return "{} ({})".format(person_name, role_name)
    return person_name


@register.filter(name="person_list")
def person_list(authors):
    """ Format a list of persons in a string enumeration"""
    return utils.person_list(authors)
