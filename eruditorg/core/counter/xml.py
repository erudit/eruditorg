# -*- coding: utf-8 -*-

from django.template import loader


def get_xml_journal_counter_report(report, organisation_name=''):
    """ Given a CounterReport instance returns the corresponding XML report. """
    # Renders the templates corresponding to the XML Counter report.
    xml_template = loader.get_template('counter/journal_report.xml')
    xml = xml_template.render({'report': report, 'organisation_name': organisation_name})
    return xml
