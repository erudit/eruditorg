import os.path as op

from django.core.exceptions import ImproperlyConfigured
from django.test.utils import override_settings
from django.test import RequestFactory
from lxml import etree as et
import pytest

from apps.webservices.views.generic import SoapWebServiceView


class TestSoapWebServiceView:
    def get_soap_request_body(self, content='', service_name='DummyService'):
        return '<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns1="{service_name}"><soapenv:Body>{content}</soapenv:Body></soapenv:Envelope>'.format(  # noqa
            content=content, service_name=service_name)

    def test_cannot_return_the_wsdl_if_the_template_name_is_not_defined(self):
        # Setup
        request = RequestFactory().get('/')

        class MyView(SoapWebServiceView):
            pass

        # Run & check
        with pytest.raises(ImproperlyConfigured):
            MyView.as_view()(request)

    def test_can_return_the_wsdl_if_the_template_name_is_defined(self):
        # Setup
        request = RequestFactory().get('/')

        class MyView(SoapWebServiceView):
            wsdl_template_name = 'dummy.wsdl'

        # Run & check
        with override_settings(
                TEMPLATES=[{
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'DIRS': ['%s/templates' % op.abspath(op.dirname(__file__))],
                    'OPTIONS': {
                        'context_processors': [
                            'django.core.context_processors.request',
                            'django.template.context_processors.debug',
                            'django.template.context_processors.request',
                            'django.template.context_processors.static',
                        ],
                    }}]):
            response = MyView.as_view()(request)
            assert response.content

    def test_requires_a_service_name(self):
        # Setup
        request = RequestFactory().post('/')

        class MyView(SoapWebServiceView):
            pass

        # Run & check
        with pytest.raises(ImproperlyConfigured):
            MyView.as_view()(request)

    def test_cannot_work_without_soap_action_header(self):
        # Setup
        request = RequestFactory().post('/')

        class MyView(SoapWebServiceView):
            service_name = 'DummyService'

        # Run & check
        response = MyView.as_view()(request)
        dom = et.fromstring(response.content)
        faultcode = dom.find('.//faultcode')
        assert faultcode.text == 'SOAP-ENV:Client'
        faultstring = dom.find('.//faultstring')
        assert faultstring.text == 'Missing HTTP_SOAPACTION header'

    def test_cannot_work_with_an_incorrect_service_name(self):
        # Setup
        request = RequestFactory().post('/', **{'HTTP_SOAPACTION': 'BadService:Test'})

        class MyView(SoapWebServiceView):
            service_name = 'DummyService'

        # Run & check
        response = MyView.as_view()(request)
        dom = et.fromstring(response.content)
        faultcode = dom.find('.//faultcode')
        assert faultcode.text == 'SOAP-ENV:Client'
        faultstring = dom.find('.//faultstring')
        assert faultstring.text == 'Incorrect service name'

    def test_cannot_work_with_an_unknown_operation_name(self):
        # Setup
        request = RequestFactory().post('/', **{'HTTP_SOAPACTION': 'DummyService:Test'})

        class MyView(SoapWebServiceView):
            service_name = 'DummyService'
            service_operations = {'dummy': 'do_dummy'}

        # Run & check
        response = MyView.as_view()(request)
        dom = et.fromstring(response.content)
        faultcode = dom.find('.//faultcode')
        assert faultcode.text == 'SOAP-ENV:Client'
        faultstring = dom.find('.//faultstring')
        assert faultstring.text == 'Unknown operation'

    def test_cannot_work_with_an_invalid_soap_env(self):
        # Setup
        data = '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"></soapenv:Envelope>'  # noqa
        request = RequestFactory().post(
            '/', data=data, content_type='text/xml', **{'HTTP_SOAPACTION': 'DummyService:dummy'})

        class MyView(SoapWebServiceView):
            service_name = 'DummyService'
            service_operations = {'dummy': 'do_dummy'}

        # Run & check
        response = MyView.as_view()(request)
        dom = et.fromstring(response.content)
        faultcode = dom.find('.//faultcode')
        assert faultcode.text == 'SOAP-ENV:Client'
        faultstring = dom.find('.//faultstring')
        assert faultstring.text == 'Unable to parse the SOAP request'

    def test_cannot_work_with_invalid_xml(self):
        # Setup
        data = '<soapenv:Envelop>T'
        request = RequestFactory().post(
            '/', data=data, content_type='text/xml', **{'HTTP_SOAPACTION': 'DummyService:dummy'})

        class MyView(SoapWebServiceView):
            service_name = 'DummyService'
            service_operations = {'dummy': 'do_dummy'}

        # Run & check
        response = MyView.as_view()(request)
        dom = et.fromstring(response.content)
        faultcode = dom.find('.//faultcode')
        assert faultcode.text == 'SOAP-ENV:Client'
        faultstring = dom.find('.//faultstring')
        assert faultstring.text == 'Unable to process the request'

    def test_cannot_allow_an_operation_that_is_not_defined(self):
        # Setup
        data = self.get_soap_request_body()
        request = RequestFactory().post(
            '/', data=data, content_type='text/xml', **{'HTTP_SOAPACTION': 'DummyService:dummy'})

        class MyView(SoapWebServiceView):
            service_name = 'DummyService'
            service_operations = {'dummy': 'do_dummy'}

        # Run & check
        with pytest.raises(ImproperlyConfigured):
            response = MyView.as_view()(request)
            print(response.content)

    def test_can_return_a_proper_soap_response(self):
        # Setup
        data = self.get_soap_request_body()
        request = RequestFactory().post(
            '/', data=data, content_type='text/xml', **{'HTTP_SOAPACTION': 'DummyService:dummy'})

        class MyView(SoapWebServiceView):
            service_name = 'DummyService'
            service_operations = {'dummy': 'do_dummy'}

            def do_dummy(self, request, body_node):
                rep = et.Element('Dummy')
                rep.text = 'Test'
                return rep

        # Run & check
        response = MyView.as_view()(request)
        dom = et.fromstring(response.content)
        dummy_node = dom.find('.//Dummy')
        assert dummy_node.text == 'Test'

    def test_returns_a_fault_server_in_case_of_implementation_error(self):
        # Setup
        data = self.get_soap_request_body()
        request = RequestFactory().post(
            '/', data=data, content_type='text/xml', **{'HTTP_SOAPACTION': 'DummyService:dummy'})

        class MyView(SoapWebServiceView):
            service_name = 'DummyService'
            service_operations = {'dummy': 'do_dummy'}

            def do_dummy(self, request, body_node):
                a = 10 / 0  # noqa

        # Run & check
        response = MyView.as_view()(request)
        dom = et.fromstring(response.content)
        faultcode = dom.find('.//faultcode')
        assert faultcode.text == 'SOAP-ENV:Server'
        faultstring = dom.find('.//faultstring')
        assert faultstring.text == 'division by zero'
