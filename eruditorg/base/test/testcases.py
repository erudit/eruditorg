from django.test import Client as ClientBase


class Client(ClientBase):
    def __init__(self, logged_user=None, **kwargs):
        super().__init__(**kwargs)
        if logged_user:
            assert self.login(
                username=logged_user.username, password=logged_user._plaintext_password
            )


def extract_post_args(dom_elem):
    """Returns a ``post()``-ready dict of all input/select values in ``dom_elem``.

    ``dom_elem`` being an element extracted from an etree-parsed DOM.

    If you have multiple forms in your response, be sure to supply a sub-element if you don't
    want all inputs in the page to be included.
    """
    result = {}
    for input in dom_elem.iterdescendants("input"):
        name = input.attrib["name"]
        value = input.attrib.get("value", "")
        if input.attrib["type"] == "checkbox":
            if not input.attrib.get("checked"):
                value = ""
            if isinstance(result.get(name, None), list):
                result[name].append(value)
            else:
                result[name] = [value]
        else:
            result[name] = value
    for k, v in list(result.items()):
        if isinstance(v, list):
            # post-process checkbox values
            if len(v) == 1:
                # single checkbox, converto into simple 'on' or '' value
                result[k] = "on" if v[0] else ""
            else:
                result[k] = {x for x in v if x}
    for select in dom_elem.iterdescendants("select"):
        options = list(select.xpath("option[@selected='selected']"))
        if "multiple" in select.attrib:
            value = [elem.get("value") for elem in options]
        else:
            try:
                value = options[0].get("value")
            except IndexError:
                value = ""
        result[select.attrib["name"]] = value
    return result
