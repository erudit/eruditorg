import pytest
from core.solrq.query import Q
from core.solrq.query import Query
from core.solrq.search import Search


class TestQ:
    def test_can_have_a_default_operator(self):
        # Run & check
        q = Q(foo="bar")
        assert q.operator == "AND"

    def test_has_no_operands_by_default(self):
        # Run & check
        q = Q(foo="bar")
        assert not len(q.operands)

    def test_saves_its_parameters(self):
        # Run & check
        q = Q(foo="bar")
        assert q.params is not None
        assert q.params["foo"] == "bar"

    def test_can_be_combined_with_another_condition_using_a_logical_or(self):
        # Run & check
        q = Q(foo="bar") | Q(foo="test")
        assert q.params is not None
        assert q.operator == "OR"
        assert len(q.operands) == 2
        assert isinstance(q.operands[0], dict)
        assert isinstance(q.operands[1], dict)
        assert len(q.operands[0]) == 1
        assert len(q.operands[1]) == 1
        assert q.operands[0]["foo"] == "bar"
        assert q.operands[1]["foo"] == "test"

    def test_can_be_combined_with_another_condition_using_a_logical_and(self):
        # Run & check
        q = Q(foo="bar") & Q(foo="test")
        assert q.params is not None
        assert q.operator == "AND"
        assert len(q.operands) == 2
        assert isinstance(q.operands[0], dict)
        assert isinstance(q.operands[1], dict)
        assert len(q.operands[0]) == 1
        assert len(q.operands[1]) == 1
        assert q.operands[0]["foo"] == "bar"
        assert q.operands[1]["foo"] == "test"

    def test_can_handle_nested_expressions(self):
        # Run & check
        q = (Q(foo="bar") | Q(foo="test")) & Q(xyz="xyz")
        assert q.params is not None
        assert q.operator == "AND"
        assert len(q.operands) == 2
        assert len(q.operands[0].operands[1]) == 1
        assert q.operands[0].operands[0]["foo"] == "bar"
        assert q.operands[0].operands[1]["foo"] == "test"

        assert isinstance(q.operands[1], dict)
        assert len(q.operands[1]) == 1
        assert q.operands[1]["xyz"] == "xyz"

    def test_cannot_be_combined_with_an_object_that_is_not_a_q_object(self):
        # Run & check
        with pytest.raises(TypeError):
            Q(foo="bar") | "dummy"

    def test_can_handle_negations(self):
        # Run & check
        q = ~Q(foo="bar")
        assert q.params is not None
        assert q.negated
        assert q.operator == "AND"
        assert len(q.operands) == 1
        assert q.operands[0]["foo"] == "bar"


class TestQuery:
    @pytest.fixture(autouse=True)
    def setUp(self, solr_client):
        self.search = Search(solr_client)

    def test_querystring_is_none_by_default(self):
        # Run & check
        query = Query(self.search)

        assert query._q is None

    def test_can_generate_correct_querystrings_using_q_objects(self):
        # Setup
        query = Query(self.search)
        # Run & check
        assert query.filter(Q(foo="bar"))._q == "(foo:bar)"
        assert query.filter(Q(foo="bar") | Q(foo="test"))._q == "((foo:bar) OR (foo:test))"
        assert query.filter(Q(foo="bar") & Q(foo="test"))._q == "((foo:bar) AND (foo:test))"
        assert (
            query.filter((Q(foo="bar") | Q(foo="test")) & Q(xyz="xyz"))._q
            == "(((foo:bar) OR (foo:test)) AND (xyz:xyz))"
        )

    def test_can_generate_correct_querystrings_using_simple_parameters(self):
        # Setup
        query = Query(self.search)
        # Run & check
        assert query.filter(foo="bar", xyz="test")._q in [
            "foo:bar AND xyz:test",
            "xyz:test AND foo:bar",
        ]

    def test_can_generate_correct_querystrings_using_q_objects_and_simple_parameters(self):
        # Setup
        query = Query(self.search)
        # Run & check
        assert (
            query.filter(Q(foo="bar") | Q(foo="test"), xyz="xyz")._q
            == "(((foo:bar) OR (foo:test))) AND (xyz:xyz)"
        )

    def test_can_generate_correct_querystrings_using_q_objects_and_negations(self):
        # We used to negate with "*:* -(term)" but that didn't yield the kind of results we wanted.
        # Using a simple NOT does the right thing. See erudit/support#209
        query = Query(self.search)
        assert (
            query.filter(Q(foo="bar") | ~Q(foo="test"), xyz="xyz")._q
            == "(((foo:bar) OR ((NOT foo:test)))) AND (xyz:xyz)"
        )

    def test_can_use_filters_mapping(self, solr_client):
        # Setup
        class NewSearch(Search):
            filters_mapping = {
                "author": "(Auteur_tri:*{author}* OR Auteur_fac:*{author}*)",
            }

        search = NewSearch(solr_client)
        query = Query(search)

        # Run & check
        assert query.filter(author="test")._q == "(Auteur_tri:*test* OR Auteur_fac:*test*)"

    def test_query_escapes_colon_character_if_search_string_is_safe(self):
        # Setup
        query = Query(self.search)
        # Run & check
        assert query.filter(Q(foo="bar : baz"), safe=True)._q == "(foo:bar \: baz)"
