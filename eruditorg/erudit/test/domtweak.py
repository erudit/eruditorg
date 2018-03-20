from collections import namedtuple

from lxml import etree
from lxml.builder import E

from eruditarticle.utils import remove_xml_namespaces


Author = namedtuple('Author', 'firstname lastname othername')


class EruditArticleTweaker:
    def __init__(self, xml):
        self.root = remove_xml_namespaces(etree.fromstring(xml))

    def set_authors(self, authors):
        # authors is a list of element with lastname/firstname/othername attributes.
        grauteur = self.root.find('.//grauteur')
        assert grauteur is not None

        def auteur(author):
            nameelems = []
            if author.firstname:
                nameelems.append(E.prenom(author.firstname))
            if author.lastname:
                nameelems.append(E.nomfamille(author.lastname))
            if author.othername:
                nameelems.append(E.autreprenom(author.othername))
            return E.auteur(E.nompers(*nameelems))

        grauteur[:] = [auteur(a) for a in authors]

    def set_author(self, firstname='', lastname='', othername=''):
        self.set_authors([Author(firstname, lastname, othername)])

    def tostring(self):
        return etree.tostring(self.root)
