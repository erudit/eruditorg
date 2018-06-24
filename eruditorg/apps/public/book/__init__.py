from .models import Book
from lxml import html as lxml_html
from django.conf import settings

books = []

if hasattr(settings, "BOOKS_DIRECTORY"):
    with open("{}/index.xml".format(settings.BOOKS_DIRECTORY), 'rb') as books_index:
        books_content = books_index.read()
        tree = lxml_html.fromstring(books_content)
        notices = tree.findall('.//div[@class="notice"]')
        for notice in notices:
            books.append(Book(notice))
