import re
from collections import namedtuple
from pathlib import Path

from django.utils.text import slugify
from lxml import etree
# noinspection PyProtectedMember
from lxml.etree import _Element as XMLElement


def get_xml_from_file(path) -> XMLElement:
    with open(str(path), 'rb') as file:
        content = file.read()
    return etree.fromstring(content, parser=etree.XMLParser(recover=True))


def stringify_children(node):
    # # https://stackoverflow.com/a/28173933/1181200
    if node is None:
        return None

    node_content = ''.join([node.text or ''] + [etree.tounicode(e) for e in node])
    return re.sub('[ \n]+', ' ', node_content)


TOCChapter = namedtuple(
    'TOCChapter',
    ('id', 'title', 'subtitle', 'authors', 'first_page',
     'last_page', 'pdf_path', 'is_section', 'is_book')
)

TOCBook = namedtuple(
    'TOCBook',
    ('id', 'title', 'subtitle', 'authors', 'first_page', 'last_page',
     'pdf_path', 'is_section', 'is_book', 'slug')
)

TOCSection = namedtuple(
    'TOCSection',
    ('title', 'level', 'is_section')
)

TableOfContents = namedtuple(
    'TableOfContents',
    ('entries', 'book_description', 'book_title', 'book_author', 'previous_chapters',
     'next_chapters', 'chapters')
)


def parse_toc_chapter(href: XMLElement, book_path: Path, book_relative_path: Path) -> TOCChapter:
    chapter_id = href[:-4]
    chapter_xml = find_chapter_xml(book_path, chapter_id)
    lang = chapter_xml.find('.//field[@name="Langue"]').text
    title_field_path = './/field[@name="Titre_{}"]'.format(lang)
    title = stringify_children(chapter_xml.find(title_field_path))
    subtitle_field_path = './/field[@name="SousTitre_{}"]'.format(lang)
    subtitle = stringify_children(chapter_xml.find(subtitle_field_path))
    authors = []
    for author_elem in chapter_xml.findall('.//field[@name="Auteur_fac"]'):
        author = stringify_children(author_elem)
        if author:
            authors.append(author)
    first_page_element = chapter_xml.find('.//field[@name="PremierePage"]')
    first_page = None if first_page_element is None else first_page_element.text
    last_page_element = chapter_xml.find('.//field[@name="DernierePage"]')
    last_page = None if last_page_element is None else last_page_element.text
    pdf_path = book_relative_path / href
    chapter = TOCChapter(
        id=chapter_id, title=title, subtitle=subtitle, authors=authors,
        first_page=first_page, last_page=last_page, pdf_path=str(pdf_path), is_section=False
    )
    return chapter


def parse_toc_book(xml: XMLElement) -> TOCBook:
    book_desc, book_title, book_author = parse_book(xml)
    return TOCBook(
        id="", title=book_title, subtitle="", authors=book_author,
        first_page="", last_page="", pdf_path="", is_book=True,
        is_section=False, slug=slugify(book_title)
    )


def parse_book(xml: XMLElement) -> tuple:
    book_desc = stringify_children(xml.find('.//div[@class="desclivre"]'))
    book_title = stringify_children(xml.find('.//h1[@class="titrelivre"]'))
    book_author = stringify_children(xml.find('.//div[@class="auteurlivre"]'))
    return book_desc, book_title, book_author


def read_toc(book_path: Path) -> TableOfContents:
    book_relative_path = book_path.relative_to(book_path.parent.parent.parent)
    xml = get_xml_from_file(book_path / 'index.xml')
    book_desc, book_title, book_author = parse_book(xml)
    toc_elements = xml.xpath('.//*[self::h3 or self::h4 or '
                             'self::div[@class="entreetdm"]]')
    toc_entries = []

    for toc_element in toc_elements:
        if toc_element.tag in ('h3', 'h4'):
            title = stringify_children(toc_element)
            toc_entries.append(TOCSection(title=title, level=toc_element.tag, is_section=True))
        else:
            href = toc_element.find('p[@class="doc"]/a')
            if href is not None:
                href = href.attrib['href']
                if href[-4:] != '.pdf':
                    raise Exception('only pdf chapters')
                toc_entry = parse_toc_chapter(href, book_path, book_relative_path)
                toc_entries.append(toc_entry)
            href = toc_element.find('p[@class="book"]/a')
            if href is not None:
                href = href.attrib['href']
                book_xml = get_xml_from_file(book_path / href)
                toc_entries.append(parse_toc_book(book_xml))
    previous_chapters = {}
    next_chapters = {}
    chapters = [entry for entry in toc_entries if not entry.is_section and not entry.is_book]
    for i, chapter in enumerate(chapters):
        if i > 0:
            previous_chapters[chapter.id] = chapters[i - 1]
        else:
            previous_chapters[chapter.id] = None
        if i < (len(chapters) - 1):
            next_chapters[chapter.id] = chapters[i + 1]
        else:
            next_chapters[chapter.id] = None

    return TableOfContents(entries=toc_entries, book_description=book_desc, book_title=book_title,
                           book_author=book_author, previous_chapters=previous_chapters,
                           next_chapters=next_chapters, chapters={c.id: c for c in chapters})


def find_chapter_xml(book_path: Path, chapter_id: str) -> XMLElement:
    xml_glob_pattern = '{}.xml'.format(chapter_id)
    glob_patterns = ['{}', 'Fiches_xml/{}', '../../fiches_solr/{}']
    for glob_pattern in glob_patterns:
        subpath_match = book_path.glob(glob_pattern.format(xml_glob_pattern))
        try:
            xml_path = next(subpath_match)
        except StopIteration:
            continue
        return get_xml_from_file(xml_path)
    raise Exception('XML for chapter {} not found !'.format(chapter_id))
