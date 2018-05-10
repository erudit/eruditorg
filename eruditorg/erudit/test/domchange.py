from collections import namedtuple

from lxml import etree
from lxml.builder import E

from eruditarticle.utils import remove_xml_namespaces


Author = namedtuple('Author', 'firstname lastname othername')
SectionTitle = namedtuple('SectionTitle', 'level paral title')


class BaseDomChanger:
    def __init__(self, xml):
        self.root = remove_xml_namespaces(etree.fromstring(xml))

    def tostring(self):
        return etree.tostring(self.root)


class EruditArticleDomChanger(BaseDomChanger):
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

    def set_section_titles(self, titles):
        grtitre = self.root.find('.//grtitre')
        REPLACE_ELEMS = {
            'surtitre', 'surtitreparal', 'surtitre2', 'surtitreparal2', 'surtitre3',
            'surtitreparal3'}
        for name in REPLACE_ELEMS:
            elem = grtitre.find(name)
            if elem is not None:
                grtitre.remove(elem)
        for title in titles:
            name = 'surtitreparal' if title.paral else 'surtitre'
            if title.level > 1:
                name += str(title.level)
            elem = etree.Element(name)
            elem.text = title.title
            grtitre.append(elem)

    def set_title(self, title):
        titre = self.root.find('.//grtitre/titre')
        titre.text = title

    def set_publication_allowed(self, publication_allowed):
        if publication_allowed:
            elem = self.root.find('.//accessible')
            if elem is not None:
                elem.parent.remove(elem)
        else:
            elem = E.accessible("non")
            self.root.getroot().append(elem)

    def set_roc(self):
        elem = self.root.find('//corps/texte')
        if elem is not None:
            elem.attrib['typetexte'] = 'roc'
        else:
            self.root.find('//corps').insert(0, E.texte(typetexte='roc'))

    def add_keywords(self, lang, keywords):
        elem = E.grmotcle(
            *[E.motcle(k) for k in keywords],
            lang=lang)
        liminaire = self.root.find('./liminaire')
        liminaire.append(elem)

    def tostring(self):
        return etree.tostring(self.root)


class EruditPublicationDomChanger(BaseDomChanger):
    def add_article(self, article):
        if self.root.find('article[idproprio="{}"]'.format(article.localidentifier)) is not None:
            return  # already there
        num_articles = len(self.root.findall('article'))
        elem = E.article(idproprio=article.localidentifier, lang='fr', ordseq=str(num_articles))
        self.root.getroot().append(elem)


class EruditJournalDomChanger(BaseDomChanger):
    def add_issue(self, issue):
        if not issue.pid:
            return
        if self.root.find('.//numero[pid="{}"]'.format(issue.pid)) is not None:
            return  # already there
        num_issues = len(self.root.findall('.//numero'))
        parentelem = self.root.find('.//decennie')
        assert parentelem is not None
        elem = E.numero(
            pid=issue.pid,
            annee=str(issue.year),
            nonumero=str(num_issues + 1),
            volume='42')
        # Publications are in reverse order
        parentelem.insert(0, elem)
