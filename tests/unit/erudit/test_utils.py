import pytest
import locale
from erudit.utils import locale_aware_sort, get_sort_key_func


try:
    locale.setlocale(locale.LC_COLLATE, 'fr_CA.UTF-8')
except locale.Error:
    has_fr_ca = False
else:
    has_fr_ca = True

needs_fr_ca = pytest.mark.skipif(not has_fr_ca, reason="Needs fr_CA.UTF-8 locale")


@needs_fr_ca
def test_locale_aware_sort():
    # We sort "naturally" in the french language.
    NAMES = ["avion", "Foulard", "épicentre", "[banquet]"]
    EXPECTED = ["avion", "[banquet]", "épicentre", "Foulard"]
    assert locale_aware_sort(NAMES) == EXPECTED


@needs_fr_ca
def test_locale_aware_sort_stopwords():
    # Names beginning with an article are ignored
    NAMES = ["L'hiver", "Poutine", "La souris", "l’apostrophe"]
    EXPECTED = ["l’apostrophe", "L'hiver", "Poutine", "La souris"]
    assert locale_aware_sort(NAMES) == EXPECTED


@needs_fr_ca
def test_locale_aware_sort_keyfunc():
    ELEMS = [('a', 'églantine'), ('b', 'à voir')]
    EXPECTED = [('b', 'à voir'), ('a', 'églantine')]
    assert locale_aware_sort(ELEMS, keyfunc=lambda x: x[1]) == EXPECTED


def test_get_sort_key_func_fr_stopwords():
    # We test that FR stopwords are properly ignored when localename is a FR one.
    f = get_sort_key_func('fr')
    assert f('le zebre') > f('souris')


def test_get_sort_key_func_no_stopwords():
    # Don't apply stopwords of a locale when another locale is specified
    f = get_sort_key_func('en')
    assert f('le zebre') < f('souris')


def test_get_sort_key_func_stopwords_order():
    # Mind your stopword order! If "Le" comes before "Les" in the list, it's going to apply first
    # and leave a "s" there.
    f = get_sort_key_func('fr')
    assert f('les arbres') < f('phronesis')


def test_get_sort_key_func_stopwords_need_space():
    # Only replace stopwords that are actually words
    f = get_sort_key_func('fr')
    assert f('lavoir') < f('phronesis')
