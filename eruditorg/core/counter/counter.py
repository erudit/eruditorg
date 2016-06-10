# -*- coding: utf-8 -*-

import calendar
import datetime as dt

from dateutil.relativedelta import relativedelta

from core.metrics.client import get_client
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

        month_periods = []
        _current_date = self.start
        while _current_date < self.end:
            _, last_month_day = calendar.monthrange(_current_date.year, _current_date.month)
            period_end = self.end if self.end.replace(day=1) == _current_date.replace(day=1) \
                else _current_date.replace(day=last_month_day)
            month_periods.append((_current_date, period_end))
            _current_date += relativedelta(months=1)
            _current_date = _current_date.replace(day=1)

        self.journal_queryset = self.filter_journal_queryset(
            journal_queryset if journal_queryset is not None
            else Journal.objects.filter(collection__localidentifier='erudit'))
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
            except IndexError:
                total_count = 0

            try:
                html_count = list(
                    self.reporting_period_html__results[
                        ('erudit__journal__article_view',
                         {'journal_localidentifier': j.localidentifier})])[0]['sum']
            except IndexError:
                html_count = 0

            try:
                pdf_count = list(
                    self.reporting_period_pdf__results[
                        ('erudit__journal__article_view',
                         {'journal_localidentifier': j.localidentifier})])[0]['sum']
            except IndexError:
                pdf_count = 0

            journal_data = {
                'localidentifier': j.localidentifier,
                'journal': j,
                'reporting_period_total': total_count,
                'reporting_period_html': html_count,
                'reporting_period_pdf': pdf_count,
                # Will be filled later on
                'months': [
                    {'start': p[0], 'end': p[1], 'count': 0, 'html_count': 0, 'pdf_count': 0}
                    for p in month_periods],
            }

            self.journals.append(journal_data)
            _journals_data_mapping.update({j.localidentifier: journal_data})

        # Processes each month one by one.
        for i, period in enumerate(month_periods):
            period_start, period_end = period

            # Fetches the results from the InfluxDB server for the current period of time.
            results = self._query(start=period_start, end=period_end)
            html_results = self._query(
                start=period_start, end=period_end, where='view_type = \'html\'')
            pdf_results = self._query(
                start=period_start, end=period_end, where='view_type = \'pdf\'')

            # Computes the total count corresponding to the returned results.
            total_count = self.get_agg_sum(results.items())
            html_total_count = self.get_agg_sum(html_results.items())
            pdf_total_count = self.get_agg_sum(pdf_results.items())

            # This value should be appended to the list of total counts per month.
            self.total['months'].append({
                'start': period_start,
                'end': period_end,
                'count': total_count,
                'html_count': html_total_count,
                'pdf_count': pdf_total_count,
            })

            # Defines the period data item that will be inserted into the 'months' list.
            period_data = {
                'start': period_start,
                'end': period_end,
                'period_title': period_start.strftime('%b-%Y'),
                'total': total_count,
                'journals': [],
            }

            # Processes each journal.
            for r in results.items():
                period_count = list(r[1])[0]['sum']
                localidentifier = r[0][1]['journal_localidentifier']
                if localidentifier in self.journal_localidentifiers:
                    period_data['journals'].append({
                        'localidentifier': localidentifier,
                        'journal': journals_dict[localidentifier],
                        'count': period_count,
                    })
                    _journals_data_mapping[localidentifier]['months'][i]['count'] = period_count
            for r in html_results.items():
                period_count = list(r[1])[0]['sum']
                localidentifier = r[0][1]['journal_localidentifier']
                if localidentifier in self.journal_localidentifiers:
                    _journals_data_mapping[localidentifier]['months'][i]['html_count'] = period_count  # noqa
            for r in pdf_results.items():
                period_count = list(r[1])[0]['sum']
                localidentifier = r[0][1]['journal_localidentifier']
                if localidentifier in self.journal_localidentifiers:
                    _journals_data_mapping[localidentifier]['months'][i]['pdf_count'] = period_count

            self.months.append(period_data)

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
        stotal = 0
        for r in results:
            if r[0][1]['journal_localidentifier'] in self.journal_localidentifiers:
                stotal += list(r[1])[0]['sum']
        return stotal

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
        where_statement = 'WHERE (time >= \'{start}\' AND time <= \'{end}\')'.format(
            start=start, end=end)

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
