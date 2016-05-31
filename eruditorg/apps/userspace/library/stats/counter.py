# -*- coding: utf-8 -*-

import calendar
import datetime as dt
import functools

from dateutil.relativedelta import relativedelta

from core.tracking.client import get_client
from erudit.models import Journal


class CounterReport(object):
    """ Performs the necessary computations to describe a Counter report.

    It uses an InfluxDB server to perform aggregations on a set of time-series data.
    """
    # These attributes should be overridden on any subclasses
    title = None
    subtitle = None

    def __init__(self, dstart, dend, journal_queryset=None):
        self.start = dstart
        self.end = dend
        rdelta = relativedelta(self.end, self.start)
        self.nmonths = rdelta.years * 12 + rdelta.months + 1
        self.journal_queryset = self.filter_journal_queryset(
            journal_queryset or Journal.objects.filter(collection__localidentifier='erudit'))
        self.journal_localidentifiers = list(
            self.journal_queryset.values_list('localidentifier', flat=True))
        self.client = get_client()

        # Pre-build a dictionnary mapping journal localidentifiers to the corresponding instances
        journals = list(self.journal_queryset)
        journals_dict = {j.localidentifier: j for j in journals}

        # Fetches the aggregations for the "total" colums
        self.reporting_period_total__results = self.fetch_reporting_period_total()
        self.reporting_period_html__results = self.fetch_reporting_period_html()
        self.reporting_period_pdf__results = self.fetch_reporting_period_pdf()

        # Initializes a dictionnary that will contain the total counts for all the columns of the
        # Counter report: Reporting Period Total, Reporting Period HTML, Reporting Period PDF and
        # total counts per month...
        self.total = {
            'reporting_period_total': self.get_agg_sum(
                self.reporting_period_total__results.items()),
            'reporting_period_html': self.get_agg_sum(self.reporting_period_html__results.items()),
            'reporting_period_pdf': self.get_agg_sum(self.reporting_period_pdf__results.items()),
            'months': [],  # The content of this list will be added later on
        }

        # Initializes a list that will contain the results of the report for each month that is
        # embedded in the considered period of time. Each element of the list will be of the form:
        #
        #     {
        #         'start': date,
        #         'end': date,
        #         'period_title': 'Jan-YYYY',
        #         'total': N,
        #         'journals': [{'localidentifier': 'XX', 'journal': Journal, 'count': N, }, ... ],
        #     }
        self.months = []

        # Initializes a list that will contains the results of the report for each journal. Each
        # element of this list will be of the forum:
        #
        #     {
        #         'localidentifier': 'XX',
        #         'journal': Journal,
        #         'reporting_period_total': N,
        #         'reporting_period_html': N,
        #         'reporting_period_pdf': N,
        #         'months': [X, Y, Z, ... ],
        #     }
        self.journals = []
        _journals_data_mapping = {}  # Used to map the journal localIDs to the aggregations results

        for j in journals:
            try:
                total_count = list(
                    self.reporting_period_total__results[
                        ('erudit__journal__article_view',
                         {'journal_localidentifier': j.localidentifier})])[0]['sum']
                html_count = list(
                    self.reporting_period_html__results[
                        ('erudit__journal__article_view',
                         {'journal_localidentifier': j.localidentifier})])[0]['sum']
                pdf_count = list(
                    self.reporting_period_pdf__results[
                        ('erudit__journal__article_view',
                         {'journal_localidentifier': j.localidentifier})])[0]['sum']
            except IndexError:
                # No aggregation results are available for this Journal instance
                total_count = 0
                html_count = 0
                pdf_count = 0

            journal_data = {
                'localidentifier': j.localidentifier,
                'journal': j,
                'reporting_period_total': total_count,
                'reporting_period_html': html_count,
                'reporting_period_pdf': pdf_count,
                'months': [0 for _ in range(self.nmonths)]  # Will be filled later on
            }

            self.journals.append(journal_data)
            _journals_data_mapping.update({j.localidentifier: journal_data})

        # Processes each month one by one.
        current_date = self.start
        i = 0
        while current_date < self.end:
            _, last_month_day = calendar.monthrange(current_date.year, current_date.month)
            period_end = self.end if self.end.replace(day=1) == current_date.replace(day=1) \
                else current_date.replace(day=last_month_day)

            # Fetches the results from the InfluxDB server for the current period of time.
            results = self._query(start=current_date, end=period_end)

            # Computes the total count corresponding to the returned results.
            total_count = self.get_agg_sum(results.items())

            # This value should be appended to the list of total counts per month.
            self.total['months'].append(total_count)

            # Defines the period data item that will be inserted into the 'months' list.
            period_data = {
                'start': current_date,
                'end': period_end,
                'period_title': current_date.strftime('%b-%Y'),
                'total': total_count,
                'journals': [],
            }

            # Processes each journal.
            for r in results.items():
                period_count = list(r[1])[0]['sum']
                localidentifier = r[0][1]['journal_localidentifier']
                period_data['journals'].append({
                    'localidentifier': localidentifier,
                    'journal': journals_dict[localidentifier],
                    'count': period_count,
                })
                _journals_data_mapping[localidentifier]['months'][i] = period_count

            self.months.append(period_data)

            current_date += relativedelta(months=1)
            current_date = current_date.replace(day=1)
            i += 1

        self.journals = sorted(self.journals, key=lambda i: i['journal'].sortable_name)

    def filter_journal_queryset(self, journal_queryset):
        """ Allows to filter the Journal queryset associated with the report. """
        return journal_queryset

    def get_additional_where_clause(self):
        """
        Provide a way to specify a WHERE clause that should be used in any query performed in the
        scope of the considered report.
        """
        return None

    def get_agg_sum(self, results):
        """ Given a list of aggregation results, returns the sum of all aggregations. """
        return functools.reduce(lambda s, result: s+list(result[1])[0]['sum'], results, 0)

    def fetch_reporting_period_total(self):
        """ Returns the results related to the 'Reporting Period Total' column. """
        return self._query()

    def fetch_reporting_period_html(self):
        """ Returns the results related to the 'Reporting Period HTML' column. """
        return self._query(where='view_type = \'html\'')

    def fetch_reporting_period_pdf(self):
        """ Returns the results related to the 'Reporting Period PDF' column. """
        return self._query(where='view_type = \'pdf\'')

    def _query(self, start=None, end=None, where=None):
        select_statement = 'SELECT SUM(num) from erudit__journal__article_view'

        start = dt.datetime.combine(start if start else self.start, dt.datetime.min.time())
        end = dt.datetime.combine(end if end else self.end, dt.datetime.max.time())
        lids_clause = ' OR '.join(
            'journal_localidentifier = \'{}\''.format(lid)
            for lid in self.journal_localidentifiers)
        where_statement = 'WHERE time >= \'{start}\' AND time <= \'{end}\' {lids}'.format(
            start=start, end=end,
            lids='AND ' + lids_clause if lids_clause else 'AND journal_localidentifier = \'none\'')

        if where:
            where_statement = '{0} AND {1}'.format(where_statement, where)

        additional_where_clause = self.get_additional_where_clause()
        if additional_where_clause:
            where_statement = '{0} AND {1}'.format(where_statement, additional_where_clause)

        groupby_statement = 'GROUP BY journal_localidentifier'
        return self.client.query(' '.join([select_statement, where_statement, groupby_statement]))


class JournalReport1(CounterReport):
    title = 'Journal Report 1 (R4)'
    subtitle = 'Number of Successful Full-Text Articles by Month and Journal'


class JournalReport1GOA(CounterReport):
    title = 'Journal Report 1 GOA (R4)'
    subtitle = 'Number of Successful Gold Open Access Full-text Article Requests by Month and Journal'  # noqa

    def filter_journal_queryset(self, journal_queryset):
        return journal_queryset.filter(open_access=True)
