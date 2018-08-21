from pathlib import Path
from apps.public.book.toc import find_chapter_xml, read_toc


FIXTURE_ROOT = Path(__file__).parent / 'fixtures'


def test_can_find_chapter_xml_when_located_in_book_directory():
    chapter_xml = find_chapter_xml(FIXTURE_ROOT / 'incantation' / '2018', '000274li')
    assert chapter_xml.find('doc/field[@name="ID"]').text == '000274li'


def test_can_find_chapter_xml_when_located_in_solr_directory():
    chapter_xml = find_chapter_xml(FIXTURE_ROOT / 'incantation' / '2018', '000275li')
    assert chapter_xml.find('doc/field[@name="ID"]').text == '000275li'


def test_can_create_section_toc_entry():
    toc = read_toc(FIXTURE_ROOT / 'incantation' / '2018')
    assert toc.entries[0].level == 'h2'
    assert toc.entries[0].title == 'Table des matières'
    assert toc.entries[0].is_section


def test_can_create_chapter_toc_entry():
    toc = read_toc(FIXTURE_ROOT / 'incantation' / '2018')
    assert toc.entries[2].title == 'Une littérature «\xA0comme incantatoire\xA0»'
    assert toc.entries[2].pdf_path == 'incantation/2018/000274li.pdf'
    assert not toc.entries[2].is_section


def test_can_preserve_markup_in_toc_text():
    toc = read_toc(FIXTURE_ROOT / 'incantation' / '2018')
    assert toc.entries[3].title == 'XIX<sup>e</sup> siècle'


def test_can_extract_book_info():
    toc = read_toc(FIXTURE_ROOT / 'incantation' / '2018')
    assert toc.book_title == "Une littérature «\xA0comme incantatoire\xA0»\xA0: aspects "\
        "et échos de l\u2019incantation en littérature (XIX<sup>e</sup>-XXI<sup>e</sup> "\
        "siècle)"
    assert toc.book_author == 'Sous la direction de Patrick Thériault'
