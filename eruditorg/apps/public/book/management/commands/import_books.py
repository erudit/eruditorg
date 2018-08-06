import re
import os
from lxml import html, etree
from bs4 import UnicodeDammit

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from apps.public.book.models import BookCollection, Book


to_import = ('ACFASSudbury','aidelf', 'artefact', 'sqrsf', 'artsVisuels', 'CEFAN', 'npqs',)

# TODO fix book import


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


class Command(BaseCommand):
    help = 'Import books from file structure'

    def add_arguments(self, parser):
        parser.add_argument('livre_directory', nargs=1, type=str)

    def import_collection(self, collection_id, notice, path):
        # TODO import the cover
        # TODO fix encoding issues
        # TODO import all child of description
        # TODO import books
        with open(path, 'rb') as index:
            root = get_unicode_root(index)
            title = _get_text(root.find('.//h1'))
            collection = BookCollection(name=title)
            description = root.find('.//div[@class="desclivre"]/p')
            if description is not None:
                collection.description = _get_text(description)
            collection.save()
            for book in root.findall('.//div[@class="entreetdm"]'):
                book_path = "{directory}/{path}".format(directory=self.directory, path=book.find('.//a').get('href').replace('html', 'xml').replace('htm', 'xml'))
                self.import_book(collection, book_path)

    def import_book(self, collection, book_path):
        if book_path.startswith('http'):
            return  # handle later
        print(book_path, os.path.exists(book_path))
        with open(book_path, 'rb') as index:
            root = get_unicode_root(index)
            book = Book()
            book.collection = collection
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
            book.title = _get_text(root.find('.//h1[@class="titrelivre"]'))
            editeur = root.find('.//h1[@class="editeur"]')
            if editeur is not None:
                book.publisher = _get_text(editeur)
            book.type = 'li'
            copyright = root.find('.//p[@class="droits"]')
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
                except:
                    print("didnt save the cover: {}".format(cover_path))
            if copyright is not None:
                book.copyright = _get_text(copyright)
            try:
                book.save()
            except:
                import ipdb; ipdb.set_trace()
        pass

    def handle(self, *args, **options):
        BookCollection.objects.all().delete()
        Book.objects.all().delete()

        self.directory = options.get('livre_directory')[0]
        self.default_collection = BookCollection(name="[Hors collection]")
        self.default_collection.save()

        with open('{directory}/livre/index.xml'.format(directory=self.directory), 'rb') as index:
            root = get_unicode_root(index)
            notices = root.findall(".//div[@class='notice']")
            for notice in notices:
                link = notice.find(".//div[@class='format']/a").get('href')
                book_id_match = re.search("/livre/([\w+]+)/.*", link)
                if book_id_match:
                    collection = book_id_match.group(1)
                    # collections have an index.xml file in their directory
                    path = "{directory}/livre/{collection}/index.xml".format(directory=self.directory, collection=collection)
                    if os.path.exists(path) and collection in to_import:
                        self.import_collection(collection, notice, path)
                    else:
                        book_path = notice.find('.//div[@class="format"]/a').get('href').replace('html', 'xml').replace(
                            'htm', 'xml').lstrip(" ")
                        book_fs_path = "{directory}/{path}".format(directory=self.directory,
                                                                   path=book_path)
                        self.import_book(self.default_collection, book_fs_path)
                else:
                    print(notice)
                    continue
                    self.import_book(self.default_collection, notice)
