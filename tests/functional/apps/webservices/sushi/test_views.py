# -*- coding: utf-8 -*-

import datetime as dt

from django.template import Context
from django.template.base import Template
from lxml import etree as et
import pytest

from erudit.test.factories import OrganisationFactory

from base.test import EruditClientTestCase
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.test.factories import JournalAccessSubscriptionPeriodFactory

from apps.webservices.sushi.views import SushiWebServiceView


REPORTREQUEST_TEMPLATE = """<?xml version='1.0' encoding='utf-8'?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
                   xmlns:counter="http://www.niso.org/schemas/counter"
                xmlns:sushi="http://www.niso.org/schemas/sushi"
                xmlns:sushicounter="http://www.niso.org/schemas/sushi/counter">
    <SOAP-ENV:Body>
        {% if not hide_reportrequest %}
        <sushicounter:ReportRequest Created="2016-06-06T18:04:28.917587+00:00"
                                    ID="0ba16cab-fc21-44ab-14d4-d72b2e124122">
            {% if not hide_requestor %}
            <sushi:Requestor>
                <sushi:ID>{{ requestor_id }}</sushi:ID>
            </sushi:Requestor>
            {% endif %}
            {% if not hide_customerreference %}
            <sushi:CustomerReference>
                <sushi:ID>{{ customer_reference }}</sushi:ID>
            </sushi:CustomerReference>
            {% endif %}
            {% if not hide_reportdefinition %}
            <sushi:ReportDefinition Name="{{ report_type|default:'JR1' }}" Release="4">
                <sushi:Filters>
                    {% if not hide_range %}
                    <sushi:UsageDateRange>
                        <sushi:Begin>{{ start }}</sushi:Begin>
                        <sushi:End>{{ end }}</sushi:End>
                    </sushi:UsageDateRange>
                    {% endif %}
                </sushi:Filters>
            </sushi:ReportDefinition>
            {% endif %}
        </sushicounter:ReportRequest>
        {% endif %}
    </SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""


class TestSushiWebServiceView(EruditClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.organisation = OrganisationFactory.create()

    def get_report_request_body(self, **kwargs):
        t = Template(REPORTREQUEST_TEMPLATE)
        c = Context(kwargs)
        return t.render(c)

    def test_cannot_handle_a_request_without_a_reportrequest(self):
        # Setup
        data = self.get_report_request_body(hide_reportrequest=True)
        request = self.factory.post(
            '/', data=data, content_type='text/xml',
            **{'HTTP_SOAPACTION': 'SushiService:GetReportIn'})
        # Run
        response = SushiWebServiceView.as_view()(request)
        # Check
        dom = et.fromstring(response.content)
        faultcode = dom.find('.//faultcode')
        assert faultcode.text == 'SOAP-ENV:Server'
        faultstring = dom.find('.//faultstring')
        assert faultstring.text == 'Invalid ReportRequest'

    def test_cannot_handle_a_request_without_a_reportdefinition(self):
        # Setup
        data = self.get_report_request_body(hide_reportdefinition=True)
        request = self.factory.post(
            '/', data=data, content_type='text/xml',
            **{'HTTP_SOAPACTION': 'SushiService:GetReportIn'})
        # Run
        response = SushiWebServiceView.as_view()(request)
        # Check
        dom = et.fromstring(response.content)
        faultcode = dom.find('.//faultcode')
        assert faultcode.text == 'SOAP-ENV:Server'
        faultstring = dom.find('.//faultstring')
        assert faultstring.text == 'Invalid ReportDefinition'

    def test_cannot_handle_a_request_without_a_range(self):
        # Setup
        data = self.get_report_request_body(hide_range=True)
        request = self.factory.post(
            '/', data=data, content_type='text/xml',
            **{'HTTP_SOAPACTION': 'SushiService:GetReportIn'})
        # Run
        response = SushiWebServiceView.as_view()(request)
        # Check
        dom = et.fromstring(response.content)
        faultcode = dom.find('.//faultcode')
        assert faultcode.text == 'SOAP-ENV:Server'
        faultstring = dom.find('.//faultstring')
        assert faultstring.text == 'Invalid range'

    def test_cannot_handle_a_request_with_a_range_containing_invalid_dates(self):
        # Setup
        data_1 = self.get_report_request_body(start='bad', end='2016-01-01')
        request_1 = self.factory.post(
            '/', data=data_1, content_type='text/xml',
            **{'HTTP_SOAPACTION': 'SushiService:GetReportIn'})
        data_2 = self.get_report_request_body(start='2016-01-01', end='bad')
        request_2 = self.factory.post(
            '/', data=data_2, content_type='text/xml',
            **{'HTTP_SOAPACTION': 'SushiService:GetReportIn'})
        # Run
        response_1 = SushiWebServiceView.as_view()(request_1)
        response_2 = SushiWebServiceView.as_view()(request_2)
        # Check
        dom_1 = et.fromstring(response_1.content)
        faultcode = dom_1.find('.//faultcode')
        assert faultcode.text == 'SOAP-ENV:Server'
        faultstring = dom_1.find('.//faultstring')
        assert faultstring.text == 'Invalid range'
        dom_2 = et.fromstring(response_2.content)
        faultcode = dom_2.find('.//faultcode')
        assert faultcode.text == 'SOAP-ENV:Server'
        faultstring = dom_2.find('.//faultstring')
        assert faultstring.text == 'Invalid range'

    def test_cannot_handle_a_request_without_a_requestor(self):
        # Setup
        data = self.get_report_request_body(
            start='2016-01-01', end='2016-02-01', hide_requestor=True)
        request = self.factory.post(
            '/', data=data, content_type='text/xml',
            **{'HTTP_SOAPACTION': 'SushiService:GetReportIn'})
        # Run
        response = SushiWebServiceView.as_view()(request)
        # Check
        dom = et.fromstring(response.content)
        faultcode = dom.find('.//faultcode')
        assert faultcode.text == 'SOAP-ENV:Server'
        faultstring = dom.find('.//faultstring')
        assert faultstring.text == 'Invalid Requestor'

    def test_cannot_handle_a_request_without_a_customer_reference(self):
        # Setup
        data = self.get_report_request_body(
            start='2016-01-01', end='2016-02-01', requestor_id=1, hide_customerreference=True)
        request = self.factory.post(
            '/', data=data, content_type='text/xml',
            **{'HTTP_SOAPACTION': 'SushiService:GetReportIn'})
        # Run
        response = SushiWebServiceView.as_view()(request)
        # Check
        dom = et.fromstring(response.content)
        faultcode = dom.find('.//faultcode')
        assert faultcode.text == 'SOAP-ENV:Server'
        faultstring = dom.find('.//faultstring')
        assert faultstring.text == 'Invalid CustomerReference'

    def test_cannot_handle_a_request_with_an_invalid_requestor_id(self):
        # Setup
        data = self.get_report_request_body(
            start='2016-01-01', end='2016-02-01', requestor_id='bad', customer_reference='1')
        request = self.factory.post(
            '/', data=data, content_type='text/xml',
            **{'HTTP_SOAPACTION': 'SushiService:GetReportIn'})
        # Run
        response = SushiWebServiceView.as_view()(request)
        # Check
        dom = et.fromstring(response.content)
        faultcode = dom.find('.//faultcode')
        assert faultcode.text == 'SOAP-ENV:Server'
        faultstring = dom.find('.//faultstring')
        assert faultstring.text == 'Invalid (Requestor ID, Customer reference)'

    def test_cannot_handle_a_request_with_an_invalid_customer_reference(self):
        # Setup
        data = self.get_report_request_body(
            start='2016-01-01', end='2016-02-01', requestor_id='1', customer_reference='bad')
        request = self.factory.post(
            '/', data=data, content_type='text/xml',
            **{'HTTP_SOAPACTION': 'SushiService:GetReportIn'})
        # Run
        response = SushiWebServiceView.as_view()(request)
        # Check
        dom = et.fromstring(response.content)
        faultcode = dom.find('.//faultcode')
        assert faultcode.text == 'SOAP-ENV:Server'
        faultstring = dom.find('.//faultstring')
        assert faultstring.text == 'Invalid (Requestor ID, Customer reference)'

    def test_cannot_handle_a_request_with_a_requestor_id_that_is_different_fro_the_customer_reference(self):  # noqa
        # Setup
        data = self.get_report_request_body(
            start='2016-01-01', end='2016-02-01', requestor_id='1', customer_reference='2')
        request = self.factory.post(
            '/', data=data, content_type='text/xml',
            **{'HTTP_SOAPACTION': 'SushiService:GetReportIn'})
        # Run
        response = SushiWebServiceView.as_view()(request)
        # Check
        dom = et.fromstring(response.content)
        faultcode = dom.find('.//faultcode')
        assert faultcode.text == 'SOAP-ENV:Server'
        faultstring = dom.find('.//faultstring')
        assert faultstring.text == 'Invalid (Requestor ID, Customer reference)'

    def test_cannot_handle_a_request_with_an_inexistant_organisation(self):
        # Setup
        data = self.get_report_request_body(
            start='2016-01-01', end='2016-02-01', requestor_id='10011', customer_reference='10011')
        request = self.factory.post(
            '/', data=data, content_type='text/xml',
            **{'HTTP_SOAPACTION': 'SushiService:GetReportIn'})
        # Run
        response = SushiWebServiceView.as_view()(request)
        # Check
        dom = et.fromstring(response.content)
        faultcode = dom.find('.//faultcode')
        assert faultcode.text == 'SOAP-ENV:Server'
        faultstring = dom.find('.//faultstring')
        assert faultstring.text == 'Unknown Requestor ID and Customer Reference'

    def test_cannot_handle_a_request_with_an_organisation_that_has_no_subscription(self):
        # Setup
        data = self.get_report_request_body(
            start='2016-01-01', end='2016-02-01', requestor_id=self.organisation.id,
            customer_reference=self.organisation.id)
        request = self.factory.post(
            '/', data=data, content_type='text/xml',
            **{'HTTP_SOAPACTION': 'SushiService:GetReportIn'})
        # Run
        response = SushiWebServiceView.as_view()(request)
        # Check
        dom = et.fromstring(response.content)
        faultcode = dom.find('.//faultcode')
        assert faultcode.text == 'SOAP-ENV:Server'
        faultstring = dom.find('.//faultstring')
        assert faultstring.text == 'Unable to find a valid subscription for the organisation'

    def test_cannot_handle_a_request_with_an_invalid_report_type(self):
        # Setup
        self.organisation.members.add(self.user)
        self.organisation.members.add(self.user)
        subscription = JournalAccessSubscriptionFactory.create(organisation=self.organisation)
        now_dt = dt.datetime.now()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))

        data = self.get_report_request_body(
            start='2016-01-01', end='2016-02-01', requestor_id=self.organisation.id,
            customer_reference=self.organisation.id, report_type='bad')
        request = self.factory.post(
            '/', data=data, content_type='text/xml',
            **{'HTTP_SOAPACTION': 'SushiService:GetReportIn'})
        # Run
        response = SushiWebServiceView.as_view()(request)
        # Check
        dom = et.fromstring(response.content)
        faultcode = dom.find('.//faultcode')
        assert faultcode.text == 'SOAP-ENV:Server'
        faultstring = dom.find('.//faultstring')
        assert faultstring.text == 'bad reports are not provided'
