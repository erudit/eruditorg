# -*- coding: utf-8 -*-

import datetime as dt

from lxml import etree as et

from core.counter.counter import JournalReport1
from core.counter.counter import JournalReport1GOA

from ..views.generic import SoapWebServiceView


class SushiWebServiceView(SoapWebServiceView):
    namespace_counter = {'url': 'http://www.niso.org/schemas/counter', 'prefix': 'c'}
    namespace_sushi = {'url': 'http://www.niso.org/schemas/sushi', 'prefix': 's'}
    namespace_sushicounter = {'url': 'http://www.niso.org/schemas/sushi/counter', 'prefix': 'sc'}

    service_name = 'SushiService'
    service_operations = {'GetReportIn': 'get_report', }
    wsdl_template_name = 'webservices/sushi/counter_sushi4_1.wsdl'

    reports_map = {
        'JR1': JournalReport1,
        'JR1 GOA': JournalReport1GOA,
    }

    def get_report(self, request, body_node):
        report_request_node = body_node.find(
            self.ns('sushicounter', 'ReportRequest'), namespaces=self.request_nsmap)
        assert report_request_node is not None, 'Invalid ReportRequest'

        report_definition_node = report_request_node.find(
            './/' + self.ns('sushi', 'ReportDefinition'), namespaces=self.request_nsmap)
        assert report_definition_node is not None, 'Invalid ReportDefinition'

        # Fetches the start date and the end date
        begin_node = report_definition_node.find(
            './/' + self.ns('sushi', 'Begin'), namespaces=self.request_nsmap)
        end_node = report_definition_node.find(
            './/' + self.ns('sushi', 'End'), namespaces=self.request_nsmap)
        assert begin_node is not None and end_node is not None, 'Invalid range'

        try:
            start_date = dt.datetime.strptime(begin_node.text, '%Y-%m-%d').date()
            end_date = dt.datetime.strptime(end_node.text, '%Y-%m-%d').date()
            assert start_date and end_date, 'Invalid range'
            assert start_date <= end_date, 'Invalid range'
        except ValueError:
            raise AssertionError('Invalid range')

        # Fetches the requestor and customer reference information
        requestor_node = report_request_node.find(
            './/' + self.ns('sushi', 'Requestor') + '/' + self.ns('sushi', 'ID'),
            namespaces=self.request_nsmap)
        assert requestor_node is not None, 'Invalid Requestor'
        customer_reference_node = report_request_node.find(
            './/' + self.ns('sushi', 'CustomerReference') + '/' + self.ns('sushi', 'ID'),
            namespaces=self.request_nsmap)
        assert requestor_node is not None, 'Invalid CustomerReference'
        requestor_id, customer_reference = requestor_node.text, customer_reference_node.text  # noqa
        # TODO: the requestor_id and the customer_reference should be used to filter the initial
        # queryset of Journal instance that is used to fetch report data. This should be done by
        # determining the subscription related with an organisation that is associated with the
        # considered requestor_id / customer_reference.

        # Generates the report
        report_code = report_definition_node.attrib['Name']
        if report_code not in self.reports_map:
            raise ValueError('{rtype} reports are not provided'.format(rtype=report_code))
        report = self.reports_map[report_code](start_date, end_date)

        # ########################## #
        # Builds the report elements #
        # ########################## #

        report_node = et.Element(self.ns('sushicounter', 'Report'))
        counter_report_node = et.SubElement(report_node, self.ns('counter', 'Report'))

        # Vendor node
        vendor_node = et.SubElement(counter_report_node, self.ns('counter', 'Vendor'))
        vendor_id_node = et.SubElement(vendor_node, self.ns('counter', 'ID'))
        vendor_id_node.text = 'ERUDIT'

        # Customer node
        customer_node = et.SubElement(counter_report_node, self.ns('counter', 'Customer'))
        customer_name_node = et.SubElement(customer_node, self.ns('counter', 'Name'))
        customer_name_node.text = 'Organisation name'  # TODO
        customer_id_node = et.SubElement(customer_node, self.ns('counter', 'ID'))
        customer_id_node.text = 'Organisation ID'  # TODO

        for jdata in report.journals:
            reportitems_node = et.SubElement(customer_node, self.ns('counter', 'ReportItems'))

            # Print ISSN node
            print_issn_node = et.SubElement(reportitems_node, self.ns('counter', 'ItemIdentifier'))
            print_issn_type_node = et.SubElement(print_issn_node, self.ns('counter', 'Type'))
            print_issn_type_node.text = 'Print_ISSN'
            print_issn_value_node = et.SubElement(print_issn_node, self.ns('counter', 'Value'))
            print_issn_value_node.text = jdata['journal'].issn_print

            # Online ISSN node
            web_issn_node = et.SubElement(reportitems_node, self.ns('counter', 'ItemIdentifier'))
            web_issn_type_node = et.SubElement(web_issn_node, self.ns('counter', 'Type'))
            web_issn_type_node.text = 'Online_ISSN'
            web_issn_value_node = et.SubElement(web_issn_node, self.ns('counter', 'Value'))
            web_issn_value_node.text = jdata['journal'].issn_web

            # DOI node
            doi_node = et.SubElement(reportitems_node, self.ns('counter', 'ItemIdentifier'))
            doi_type_node = et.SubElement(doi_node, self.ns('counter', 'Type'))
            doi_type_node.text = 'DOI'
            doi_value_node = et.SubElement(doi_node, self.ns('counter', 'Value'))
            doi_value_node.text = '--'  # TODO

            # Platform, publisher, type and name nodes
            platform_node = et.SubElement(reportitems_node, self.ns('counter', 'ItemPlatform'))
            platform_node.text = 'Erudit'
            publisher_node = et.SubElement(reportitems_node, self.ns('counter', 'ItemPublisher'))
            publisher_node.text = str(jdata['journal'].publishers.first())
            name_node = et.SubElement(reportitems_node, self.ns('counter', 'ItemName'))
            name_node.text = jdata['journal'].name
            datatype_node = et.SubElement(reportitems_node, self.ns('counter', 'ItemDataType'))
            datatype_node.text = 'Journal'

            # Global ItemPerformance node
            g_perf_node = et.SubElement(reportitems_node, self.ns('counter', 'ItemPerformance'))
            g_period_node = et.SubElement(g_perf_node, self.ns('counter', 'Period'))
            g_begin_node = et.SubElement(g_period_node, self.ns('counter', 'Begin'))
            g_begin_node.text = report.start.strftime('%Y-%m-%d')
            g_end_node = et.SubElement(g_period_node, self.ns('counter', 'End'))
            g_end_node.text = report.end.strftime('%Y-%m-%d')
            g_category_node = et.SubElement(g_perf_node, self.ns('counter', 'Category'))
            g_category_node.text = 'Requests'
            g_ft_total_node = et.SubElement(g_perf_node, self.ns('counter', 'Instance'))
            g_ft_total_type_node = et.SubElement(g_ft_total_node, self.ns('counter', 'MetricType'))
            g_ft_total_type_node.text = 'ft_total'
            g_ft_total_count_node = et.SubElement(g_ft_total_node, self.ns('counter', 'Count'))
            g_ft_total_count_node.text = str(jdata['reporting_period_total'])
            g_ft_html_node = et.SubElement(g_perf_node, self.ns('counter', 'Instance'))
            g_ft_html_type_node = et.SubElement(g_ft_html_node, self.ns('counter', 'MetricType'))
            g_ft_html_type_node.text = 'ft_html'
            g_ft_html_count_node = et.SubElement(g_ft_html_node, self.ns('counter', 'Count'))
            g_ft_html_count_node.text = str(jdata['reporting_period_html'])
            g_ft_pdf_node = et.SubElement(g_perf_node, self.ns('counter', 'Instance'))
            g_ft_pdf_type_node = et.SubElement(g_ft_pdf_node, self.ns('counter', 'MetricType'))
            g_ft_pdf_type_node.text = 'ft_pdf'
            g_ft_pdf_count_node = et.SubElement(g_ft_pdf_node, self.ns('counter', 'Count'))
            g_ft_pdf_count_node.text = str(jdata['reporting_period_pdf'])

            # Processes each month
            for month in jdata['months']:
                l_perf_node = et.SubElement(
                    reportitems_node, self.ns('counter', 'ItemPerformance'))
                l_period_node = et.SubElement(l_perf_node, self.ns('counter', 'Period'))
                l_begin_node = et.SubElement(l_period_node, self.ns('counter', 'Begin'))
                l_begin_node.text = month['start'].strftime('%Y-%m-%d')
                l_end_node = et.SubElement(l_period_node, self.ns('counter', 'End'))
                l_end_node.text = month['end'].strftime('%Y-%m-%d')
                l_category_node = et.SubElement(l_perf_node, self.ns('counter', 'Category'))
                l_category_node.text = 'Requests'
                l_ft_total_node = et.SubElement(l_perf_node, self.ns('counter', 'Instance'))
                l_ft_total_type_node = et.SubElement(
                    l_ft_total_node, self.ns('counter', 'MetricType'))
                l_ft_total_type_node.text = 'ft_total'
                l_ft_total_count_node = et.SubElement(l_ft_total_node, self.ns('counter', 'Count'))
                l_ft_total_count_node.text = str(month['count'])
                l_ft_html_node = et.SubElement(l_perf_node, self.ns('counter', 'Instance'))
                l_ft_html_type_node = et.SubElement(
                    l_ft_html_node, self.ns('counter', 'MetricType'))
                l_ft_html_type_node.text = 'ft_html'
                l_ft_html_count_node = et.SubElement(l_ft_html_node, self.ns('counter', 'Count'))
                l_ft_html_count_node.text = str(month['html_count'])
                l_ft_pdf_node = et.SubElement(l_perf_node, self.ns('counter', 'Instance'))
                l_ft_pdf_type_node = et.SubElement(l_ft_pdf_node, self.ns('counter', 'MetricType'))
                l_ft_pdf_type_node.text = 'ft_pdf'
                l_ft_pdf_count_node = et.SubElement(l_ft_pdf_node, self.ns('counter', 'Count'))
                l_ft_pdf_count_node.text = str(month['pdf_count'])

        report_response_node = et.Element(self.ns('sushicounter', 'ReportResponse'))
        report_response_node.append(report_definition_node)
        report_response_node.append(report_node)

        return report_response_node
