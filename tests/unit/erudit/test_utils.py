import pytest
from erudit.utils import locale_aware_sort, get_sort_key_func, pairify, catch_and_log, qs_cache_key
from erudit.test import needs_fr_ca
from erudit.test.factories import JournalFactory, IssueFactory


@needs_fr_ca
def test_locale_aware_sort():
    # We sort "naturally" in the french language.
    NAMES = ["avion", "Foulard", "épicentre", "[banquet]"]
    EXPECTED = ["avion", "[banquet]", "épicentre", "Foulard"]
    assert locale_aware_sort(NAMES) == EXPECTED


@needs_fr_ca
def test_locale_aware_sort_stopwords():
    # Names beginning with an article are ignored
    NAMES = ["L'hiver", "Poutine", "La souris", "l’apostrophe", "The international"]
    EXPECTED = ["l’apostrophe", "L'hiver", "The international", "Poutine", "La souris"]
    assert locale_aware_sort(NAMES) == EXPECTED


@needs_fr_ca
def test_locale_aware_sort_keyfunc():
    ELEMS = [("a", "églantine"), ("b", "à voir")]
    EXPECTED = [("b", "à voir"), ("a", "églantine")]
    assert locale_aware_sort(ELEMS, keyfunc=lambda x: x[1]) == EXPECTED


def test_get_sort_key_func_fr_stopwords():
    # We test that FR stopwords are properly ignored when localename is a FR one.
    f = get_sort_key_func("fr")
    assert f("le zebre") > f("souris")


def test_get_sort_key_func_no_stopwords():
    # Don't apply stopwords of a locale when another locale is specified
    f = get_sort_key_func("en")
    assert f("le zebre") < f("souris")


def test_get_sort_key_func_stopwords_order():
    # Mind your stopword order! If "Le" comes before "Les" in the list, it's going to apply first
    # and leave a "s" there.
    f = get_sort_key_func("fr")
    assert f("les arbres") < f("phronesis")


def test_get_sort_key_func_stopwords_need_space():
    # Only replace stopwords that are actually words
    f = get_sort_key_func("fr")
    assert f("lavoir") < f("phronesis")


def test_pairify():
    assert list(pairify(["foo", 1, "bar", 2])) == [("foo", 1), ("bar", 2)]


def test_catch_and_log(caplog):
    @catch_and_log
    def zerodiv():
        return 1 / 0

    assert zerodiv() is None
    assert "ZeroDivisionError" in caplog.text


@pytest.mark.django_db
def test_qs_cache_key():
    journal = JournalFactory()
    issues = IssueFactory.create_batch(5, journal=journal)
    cache_key = qs_cache_key(journal.issues.all())
    assert cache_key == "1,2,3,4,5"
