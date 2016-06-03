# -*- coding: utf-8 -*-

import datetime as dt


def get_csv_journal_counter_report_rows(report, organisation_name=''):
    """ Given a CounterReport instance returns the a list of rows that can be written to a CSV. """
    rows = []

    # Add the header rows
    rows.append([report.title, report.subtitle])
    rows.append([organisation_name])
    rows.append([])
    rows.append(['Period covered by Report'])
    rows.append(['{start} to {end}'.format(
        start=report.start.isoformat(), end=report.end.isoformat())])
    rows.append(['Date run'])
    rows.append([dt.datetime.now().isoformat()])

    # Add the sub-header row
    rows.append([
        'Journal', 'Publisher', 'Platform', 'Journal DOI', 'Proprietary Identifier',
        'Print ISSN', 'Online ISSN', 'Reporting Period Total', 'Reporting Period HTML',
        'Reporting Period PDF',
    ] + [m['period_title'] for m in report.months])

    # Add the "total" row
    rows.append([
        'Total for all journals',
        '',  # Publisher
        '',  # Platform
        '',  # Journal DOI
        '',  # Proprietary Identifier
        '',  # Print ISSN
        '',  # Online ISSN
        report.total['reporting_period_total'],
        report.total['reporting_period_html'],
        report.total['reporting_period_pdf'],
    ] + [m['count'] for m in report.total['months']])

    for jdata in report.journals:
        rows.append([
            jdata['journal'].name,
            jdata['journal'].publishers.first(),
            jdata['journal'].collection.name,
            '',  # Journal DOI
            '',  # Proprietary Identifier
            jdata['journal'].issn_print,
            jdata['journal'].issn_web,
            jdata['reporting_period_total'],
            jdata['reporting_period_html'],
            jdata['reporting_period_pdf'],
        ] + [m['count'] for m in jdata['months']])

    return rows
