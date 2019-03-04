from pathlib import Path
from apps.public.book.toc import find_chapter_xml, read_toc


FIXTURE_ROOT = Path(__file__).parent / 'fixtures'


def test_can_find_chapter_xml_when_located_in_book_subdirectory():
    chapter_xml = find_chapter_xml(FIXTURE_ROOT / 'incantation' / '2018', '000274li')
    assert chapter_xml.find('doc/field[@name="ID"]').text == '000274li'


def test_can_find_chapter_xml_when_located_in_solr_directory():
    chapter_xml = find_chapter_xml(FIXTURE_ROOT / 'incantation' / '2018', '000275li')
    assert chapter_xml.find('doc/field[@name="ID"]').text == '000275li'


def test_can_find_chapter_xml_when_located_in_book_directory():
    chapter_xml = find_chapter_xml(FIXTURE_ROOT / 'incantation' / '2018', '000276li')
    assert chapter_xml.find('doc/field[@name="ID"]').text == '000276li'


def test_can_create_book_toc_entry():
    toc = read_toc(FIXTURE_ROOT / 'subbook')
    assert toc.entries[1].is_book


def test_can_create_section_toc_entry():
    toc = read_toc(FIXTURE_ROOT / 'incantation' / '2018')
    assert toc.entries[0].level == 'h3'
    assert toc.entries[0].title == 'Introduction'
    assert toc.entries[0].is_section


def test_can_create_chapter_toc_entry():
    toc = read_toc(FIXTURE_ROOT / 'incantation' / '2018')
    assert toc.entries[1].title == 'Une littérature «\xA0comme incantatoire\xA0»'
    assert toc.entries[1].subtitle == 'Le cas exemplaire de la modernité symboliste'
    assert toc.entries[1].pdf_path == 'fixtures/incantation/2018/000274li.pdf'
    assert not toc.entries[1].is_section


def test_can_preserve_markup_in_toc_text():
    toc = read_toc(FIXTURE_ROOT / 'incantation' / '2018')
    assert toc.entries[2].title == 'XIX<sup>e</sup> siècle'


def test_can_extract_book_info():
    toc = read_toc(FIXTURE_ROOT / 'incantation' / '2018')
    assert toc.book_title == "Une littérature «\xA0comme incantatoire\xA0»\xA0: aspects "\
        "et échos de l\u2019incantation en littérature (XIX<sup>e</sup>-XXI<sup>e</sup> "\
        "siècle)"
    assert toc.book_author == 'Sous la direction de Patrick Thériault'


def test_can_give_none_as_previous_chapter_for_first_chapter():
    toc = read_toc(FIXTURE_ROOT / 'incantation' / '2018')
    assert toc.previous_chapters['000274li'] is None


def test_can_give_previous_chapter():
    toc = read_toc(FIXTURE_ROOT / 'incantation' / '2018')
    assert toc.previous_chapters['000275li'].id == '000274li'


def test_can_give_none_as_next_chapter_for_last_chapter():
    toc = read_toc(FIXTURE_ROOT / 'incantation' / '2018')
    assert toc.next_chapters['000285li'] is None


def test_can_give_next_chapter():
    toc = read_toc(FIXTURE_ROOT / 'incantation' / '2018')
    assert toc.next_chapters['000274li'].id == '000275li'
