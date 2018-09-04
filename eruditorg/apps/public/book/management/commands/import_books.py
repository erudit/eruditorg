import re
from pathlib import Path

from django.utils.text import slugify
from lxml import html
# noinspection PyProtectedMember
from bs4 import UnicodeDammit

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from apps.public.book.models import BookCollection, Book


to_import = ('ACFASSudbury', 'aidelf', 'artefact', 'sqrsf', 'artsVisuels', 'CEFAN', 'npqs', )


def get_unicode_root(fd):
    content = fd.read()
    doc = UnicodeDammit(content, is_html=True)
    parser = html.HTMLParser(encoding=doc.original_encoding)
    root = html.document_fromstring(content, parser=parser)
    return root


def _get_text(node):
    if node is None:
        return None
    return " ".join(node.text_content().split())


def _get_by_label(root_node, label):
    nodes = root_node.xpath(
        './/text[text()="{}"]'.format(label),
        namespaces={'i18n': 'http://apache.org/cocoon/i18n/2.1'})
    if len(nodes) and nodes[0].tail:
        return nodes[0].tail
    else:
        return None


def cleanup_isbn(isbn):
    return re.sub('[^0-9\-X]', '', isbn)


def extract_ibsn_from_book_index(root):
    digital_isbn = isbn = None
    isbn_nodes = root.xpath('.//div[@class="editeur" and starts-with(., "ISBN")]')
    if len(isbn_nodes):
        isbn_text = " ".join(isbn_nodes[0].text_content().split())
        isbns = isbn_text.split(';')
        for isbn_str in isbns:
            if 'PDF' in isbn_str:
                digital_isbn = cleanup_isbn(isbn_str)
            else:
                isbn = cleanup_isbn(isbn_str)
    return digital_isbn, isbn


class Command(BaseCommand):
    help = 'Import books from file structure'

    def add_arguments(self, parser):
        parser.add_argument('livre_directory', nargs=1, type=str)

    def import_collection(self, path):
        with open(str(self.directory / path), 'rb') as index:
            root = get_unicode_root(index)
            title = _get_text(root.find('.//h1'))
            collection = BookCollection(name=title, path=path.parent, slug=slugify(title))
            description = root.find('.//div[@class="desclivre"]/p')
            if description is not None:
                collection.description = _get_text(description)
            collection.save()
            for book in root.findall('.//div[@class="entreetdm"]'):
                subpath = book.find('.//a').get('href').replace('html', 'xml').replace('htm', 'xml')
                self.import_book(collection, Path(subpath.lstrip(' /')), None)

    def import_book(self, collection, book_path, book_notice):
        full_path = self.directory / book_path
        print(full_path, full_path.exists())
        with open(str(full_path), 'rb') as index:
            root = get_unicode_root(index)
            book = Book(collection=collection, path=book_path.parent)
            authors = root.findall('.//div[@class="auteurtdm"]')
            if len(authors) > 0:
                book.authors = _get_text(authors[0])
                if len(authors) > 1:
                    book.contributors = _get_text(authors[1])
            else:
                authors = root.findall('.//div[@class="auteurlivre"]')
                if authors is not None and len(authors) > 0:
                    book.authors = _get_text(authors[0])
                    if len(authors) > 1:
                        book.contributors = _get_text(authors[1])
            if book_notice:
                book.title = _get_text(book_notice.find('.//div[@class="texte"]/p[@class="titre"]'))
                book.subtitle = _get_text(
                    book_notice.find('.//div[@class="texte"]/p[@class="sstitre"]'))
                year = _get_by_label(book_notice, 'anneepublication')
                if year:
                    book.year = re.sub('[^0-9]', '', year)
                digital_isbn, isbn = extract_ibsn_from_book_index(root)
                if not isbn:
                    isbn = _get_by_label(book_notice, 'isbn')
                    if isbn:
                        isbn = cleanup_isbn(isbn)
                if not digital_isbn:
                    digital_isbn = _get_by_label(book_notice, 'isbnnumerique')
                    if not digital_isbn:
                        digital_isbn = _get_by_label(book_notice, 'ISBN PDF')

                    if digital_isbn:
                        digital_isbn = cleanup_isbn(digital_isbn)
                book.isbn = isbn
                book.digital_isbn = digital_isbn
                publisher_tag = book_notice.find('.//div[@class="texte"]/p/a')
                if publisher_tag is not None:
                    href = publisher_tag.attrib['href']
                    text = _get_text(publisher_tag)
                    if href:
                        book.publisher_url = href
                    if text:
                        book.publisher = text
                copyrights = book_notice.xpath('.//p[starts-with(., "©")]')
                if len(copyrights):
                    book.copyright = _get_text(copyrights[0])
            else:
                book.title = _get_text(root.find('.//h1[@class="titrelivre"]'))
                digital_isbn, isbn = extract_ibsn_from_book_index(root)
                book.digital_isbn = digital_isbn
                book.isbn = isbn
                copyright_node = root.find('.//div[@class="piedlivre"]/p')
                if copyright_node is not None:
                    book.copyright = _get_text(copyright_node)

            slug = slugify(book.title)
            if book.isbn or book.digital_isbn:
                slug = '{}--{}'.format(slug, book.digital_isbn or book.isbn)
            book.slug = slug
            editeur = root.find('.//h1[@class="editeur"]')
            if editeur is not None:
                book.publisher = _get_text(editeur)
            book.type = 'li' if book_notice is not None else 'ac'
            copyright_ = root.find('.//p[@class="droits"]')
            cover = root.find('.//div[@class="couverture"]/img')
            if cover is not None:
                src = cover.get('src')
                cover_path = '{root}/{path}'.format(
                    root=self.directory,
                    path=src
                )
                try:
                    bla = default_storage.save('book_cover', open(cover_path, 'rb'))
                    book.cover = bla
                    print("saved the cover: {}".format(cover_path))
                except FileNotFoundError:
                    print("didnt save the cover: {}".format(cover_path))
            if copyright_ is not None:
                book.copyright = _get_text(copyright_)
            book.save()

    def handle(self, *args, **options):
        BookCollection.objects.all().delete()
        Book.objects.all().delete()

        # noinspection PyAttributeOutsideInit
        self.directory = Path(options.get('livre_directory')[0])
        default_collection = BookCollection.objects.create(name="[Hors collection]")

        with open('{directory}/livre/index.xml'.format(directory=self.directory), 'rb') as index:
            root = get_unicode_root(index)
            notices = root.findall(".//div[@class='notice']")
            for notice in notices:
                link = notice.find(".//div[@class='format']/a").get('href')
                book_id_match = re.search("/livre/([\w+]+)/.*", link)
                if book_id_match:
                    collection = book_id_match.group(1)
                    # collections have an index.xml file in their directory
                    path = Path("livre/{collection}/index.xml".format(collection=collection))
                    if (self.directory / path).exists() and collection in to_import:
                        self.import_collection(path)
                    else:
                        book_path = notice.find('.//div[@class="format"]/a').get('href')
                        book_path = book_path.replace('html', 'xml').replace('htm', 'xml')
                        self.import_book(default_collection, Path(book_path.lstrip(" /")), notice)
                else:
                    print(notice)
                    continue
