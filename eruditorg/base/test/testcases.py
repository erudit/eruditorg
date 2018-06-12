from django.test import Client as ClientBase


class Client(ClientBase):
    def __init__(self, logged_user=None, **kwargs):
        super().__init__(**kwargs)
        if logged_user:
            assert self.login(
                username=logged_user.username, password=logged_user._plaintext_password)


def extract_post_args(dom_elem):
    """Returns a ``post()``-ready dict of all input/select values in ``dom_elem``.

    ``dom_elem`` being an element extracted from an etree-parsed DOM.

    If you have multiple forms in your response, be sure to supply a sub-element if you don't
    want all inputs in the page to be included.
    """
    result = {}
    for input in dom_elem.iterdescendants('input'):
        if input.attrib['type'] == 'checkbox':
            value = 'on' if input.attrib.get('checked') else ''
        else:
            value = input.attrib.get('value', '')
        result[input.attrib['name']] = value
    for select in dom_elem.iterdescendants('select'):
        options = list(select.xpath('option[@selected=\'selected\']'))
        if 'multiple' in select.attrib:
            value = [elem.get('value') for elem in options]
        else:
            try:
                value = options[0].get('value')
            except IndexError:
                value = ''
        result[select.attrib['name']] = value
    return result
