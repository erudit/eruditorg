from erudit.templatetags.model_formatters import person_list, format_editor


def test_can_format_the_output_of_liberuditarticle(eruditarticle):
    # should not crash
    for author in eruditarticle.get_authors():
        format_editor(author)


def test_can_format_an_empty_list():
    assert person_list([]) == ""


def test_can_format_single_author():
    assert person_list(["Paul"]) == "Paul"


def test_can_format_two_authors():
    authors = ["Paul", "Paul"]
    assert person_list(authors) == "Paul et Paul"
    assert person_list(authors) == "Paul et Paul"


def test_can_format_n_authors():
    assert person_list(["Paul", "Paul", "Georges"]) == "Paul, Paul et Georges"
