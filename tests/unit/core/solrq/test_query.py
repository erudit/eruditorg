# -*- coding: utf-8 -*-

from core.solrq.query import Q
from core.solrq.query import Query
from core.solrq.search import Search
from core.solrq.test import SolrqTestCase


class TestQ(SolrqTestCase):
    def test_can_have_a_default_operator(self):
        # Run & check
        q = Q(foo='bar')
        self.assertEqual(q.operator, 'AND')

    def test_has_no_operands_by_default(self):
        # Run & check
        q = Q(foo='bar')
        self.assertFalse(len(q.operands))

    def test_saves_its_parameters(self):
        # Run & check
        q = Q(foo='bar')
        self.assertTrue(q.params is not None)
        self.assertEqual(q.params['foo'], 'bar')

    def test_can_be_combined_with_another_condition_using_a_logical_or(self):
        # Run & check
        q = Q(foo='bar') | Q(foo='test')
        self.assertTrue(q.params is not None)
        self.assertEqual(q.operator, 'OR')
        self.assertEqual(len(q.operands), 2)
        self.assertTrue(isinstance(q.operands[0], dict))
        self.assertTrue(isinstance(q.operands[1], dict))
        self.assertEqual(len(q.operands[0]), 1)
        self.assertEqual(len(q.operands[1]), 1)
        self.assertEqual(q.operands[0]['foo'], 'bar')
        self.assertEqual(q.operands[1]['foo'], 'test')

    def test_can_be_combined_with_another_condition_using_a_logical_and(self):
        # Run & check
        q = Q(foo='bar') & Q(foo='test')
        self.assertTrue(q.params is not None)
        self.assertEqual(q.operator, 'AND')
        self.assertEqual(len(q.operands), 2)
        self.assertTrue(isinstance(q.operands[0], dict))
        self.assertTrue(isinstance(q.operands[1], dict))
        self.assertEqual(len(q.operands[0]), 1)
        self.assertEqual(len(q.operands[1]), 1)
        self.assertEqual(q.operands[0]['foo'], 'bar')
        self.assertEqual(q.operands[1]['foo'], 'test')

    def test_can_handle_nested_expressions(self):
        # Run & check
        q = (Q(foo='bar') | Q(foo='test')) & Q(xyz='xyz')
        self.assertTrue(q.params is not None)
        self.assertEqual(q.operator, 'AND')
        self.assertEqual(len(q.operands), 2)
        self.assertEqual(len(q.operands[0].operands[1]), 1)
        self.assertEqual(q.operands[0].operands[0]['foo'], 'bar')
        self.assertEqual(q.operands[0].operands[1]['foo'], 'test')

        self.assertTrue(isinstance(q.operands[1], dict))
        self.assertEqual(len(q.operands[1]), 1)
        self.assertEqual(q.operands[1]['xyz'], 'xyz')

    def test_cannot_be_combined_with_an_object_that_is_not_a_q_object(self):
        # Run & check
        with self.assertRaises(TypeError):
            Q(foo='bar') | 'dummy'  # noqa

    def test_can_handle_negations(self):
        # Run & check
        q = ~Q(foo='bar')
        self.assertTrue(q.params is not None)
        self.assertTrue(q.negated)
        self.assertEqual(q.operator, 'AND')
        self.assertEqual(len(q.operands), 1)
        self.assertEqual(q.operands[0]['foo'], 'bar')


class TestQuery(SolrqTestCase):
    def setUp(self):
        super(TestQuery, self).setUp()
        self.search = Search(self.client)

    def test_querystring_is_none_by_default(self):
        # Run & check
        query = Query(self.search)

        self.assertEqual(query._q, None)

    def test_can_generate_correct_querystrings_using_q_objects(self):
        # Setup
        query = Query(self.search)
        # Run & check
        self.assertEqual(
            query.filter(Q(foo='bar'))._q,
            '(foo:bar)')
        self.assertEqual(
            query.filter(Q(foo='bar') | Q(foo='test'))._q,
            '((foo:bar) OR (foo:test))')
        self.assertEqual(
            query.filter(Q(foo='bar') & Q(foo='test'))._q,
            '((foo:bar) AND (foo:test))')
        self.assertEqual(
            query.filter((Q(foo='bar') | Q(foo='test')) & Q(xyz='xyz'))._q,
            '(((foo:bar) OR (foo:test)) AND (xyz:xyz))')

    def test_can_generate_correct_querystrings_using_simple_parameters(self):
        # Setup
        query = Query(self.search)
        # Run & check
        self.assertTrue(
            query.filter(foo='bar', xyz='test')._q in
            ['foo:bar AND xyz:test', 'xyz:test AND foo:bar'])

    def test_can_generate_correct_querystrings_using_q_objects_and_simple_parameters(self):
        # Setup
        query = Query(self.search)
        # Run & check
        self.assertEqual(
            query.filter(Q(foo='bar') | Q(foo='test'), xyz='xyz')._q,
            '(((foo:bar) OR (foo:test))) AND (xyz:xyz)')

    def test_can_generate_correct_querystrings_using_q_objects_and_negations(self):
        # We used to negate with "*:* -(term)" but that didn't yield the kind of results we wanted.
        # Using a simple NOT does the right thing. See erudit/support#209
        query = Query(self.search)
        self.assertEqual(
            query.filter(Q(foo='bar') | ~Q(foo='test'), xyz='xyz')._q,
            '(((foo:bar) OR ((NOT foo:test)))) AND (xyz:xyz)')

    def test_can_use_filters_mapping(self):
        # Setup
        class NewSearch(Search):
            filters_mapping = {
                'author': '(Auteur_tri:*{author}* OR Auteur_fac:*{author}*)',
            }

        search = NewSearch(self.client)
        query = Query(search)

        # Run & check
        self.assertEqual(
            query.filter(author='test')._q,
            '(Auteur_tri:*test* OR Auteur_fac:*test*)')
