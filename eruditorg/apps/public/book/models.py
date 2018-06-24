from lxml import etree as et


class Book:

    def __init__(self, root):
        self.root = root

    def _get_text(self, xpath):
        node = self.root.find(xpath)
        if node is not None:
            et.strip_tags(node, "*")
            return node.text

    def get_title(self):
        return self._get_text('.//p[@class="titre"]')

    def get_subtitle(self):
        return self._get_text('.//p[@class="sstitre"]')

    def get_subtitle2(self):
        return self._get_text('.//p[@class="sstitre2"]')

    def get_isbn(self):
        return self._get_text('.//p[@class="isbn"]')

    def get_digital_isbn(self):
        return self._get_text('.//p[@class="isbnnumerique"]')

    def get_year(self):
        return self._get_text('.//p[@class="anneepublication"]')

    def get_authors(self):
        return self._get_text('.//p[@class="auteur"]')

    def get_copyright(self):
        return self._get_text('.//p[@class="droitauteur"]')
