# -*- coding: utf-8 -*-

import inspect
import structlog

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.template import loader
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.functional import cached_property
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from lxml import etree as et

logger = structlog.getLogger(__name__)


class SoapWebServiceView(View):
    """ This views can be used to define SOAP web services. """
    http_method_names = ['get', 'post', ]

    namespace_soap = {'url': 'http://schemas.xmlsoap.org/soap/envelope/', 'prefix': 'SOAP-ENV'}
    namespace_xsd = {'url': 'http://www.w3.org/1999/XMLSchema', 'prefix': 'xsd'}
    namespace_xsi = {'url': 'http://www.w3.org/1999/XMLSchema-instance', 'prefix': 'xsi'}

    # ############################################################# #
    # The following attributes should be overriden on any subclass! #
    # ############################################################# #

    # Defines the location of the WSDL associated with the web service.
    wsdl_template_name = None

    # The service name is the name of the service ; it will be referenced SOAPAction header.
    # eg. "SOAPAction:[service_name]:[operation_name]"
    service_name = None

    # The following dictionary should allow the correspondence between a SOAP operation name and a
    # corresponding view method to execute. Each method corresponding to an operation should take a
    # single argument: the lxml Element instance corresponding to the SOAP Body.
    # eg. {'MyOperation': 'my_operation_method', }
    service_operations = {}

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SoapWebServiceView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        if self.wsdl_template_name is None:
            raise ImproperlyConfigured(
                '{cls} is missing a WSDL template name. '
                'Please define {cls}.wsdl_template_name'.format(cls=self.__class__.__name__))
        wsdl_template = loader.get_template(self.wsdl_template_name)
        response = HttpResponse(wsdl_template.render({}), content_type='text/xml')
        return response

    def get_soap_envelope(self, xml_node):
        """ Given a lxml Element, wraps it under a SOAP Envelope and a SOAP body nodes. """
        soap_env = et.Element(self.ns('soap', 'Envelope'), nsmap=self.nsmap)
        soap_body = et.SubElement(soap_env, self.ns('soap', 'Body'))
        soap_body.append(xml_node)
        return soap_env

    def ns(self, ns, tag_name):
        """ Formats the given tag using the considered namespace. """
        ns = getattr(self, 'namespace_' + ns)
        return '{{{ns}}}{tag_name}'.format(ns=ns['url'], tag_name=tag_name)

    @cached_property
    def nsmap(self):
        """ This property returns the namespace dictionary.

        It constructs a dictionary mapping namespace prefixes to their corresponding urls. It can be
        used when building SOAP operation responses.
        """
        vattrs = inspect.getmembers(self.__class__, lambda a: not(inspect.isroutine(a)))
        return {a[1]['prefix']: a[1]['url'] for a in vattrs if a[0].startswith('namespace_')}

    def post(self, request):
        if self.service_name is None:
            raise ImproperlyConfigured(
                '{cls} is missing a service name. '
                'Please define {cls}.service_name'.format(cls=self.__class__.__name__))

        # Tries to fetch the considered operation name and processes to some validations. Then Tries
        # to parse the input XML and fetch the SOAP body node.
        try:
            soap_action = request.META.get('HTTP_SOAPACTION', None)
            assert soap_action is not None, 'Missing HTTP_SOAPACTION header'
            service_name, operation_name = soap_action.replace('"', '').split(':')
            assert service_name == self.service_name, 'Incorrect service name'
            assert operation_name in self.service_operations, 'Unknown operation'
            dom = et.fromstring(request.body)
            body_node = dom.find('.//' + self.ns('soap', 'Body'), namespaces=dom.nsmap)
            assert body_node is not None, 'Unable to parse the SOAP request'
        except AssertionError as e:
            return self.soap_fault_client(e.args[0])
        except et.XMLSyntaxError:
            return self.soap_fault_client('Unable to process the request')

        # Attaches the dom lxml object and input nsmap to the view object so that operation methods
        # can use them to perform further operations on the input XML tree.
        self.dom = dom
        self.request_nsmap = dom.nsmap

        # Fetches the method associated with the current operation.
        try:
            exec_operation = getattr(self, self.service_operations[operation_name])
        except AttributeError:
            raise ImproperlyConfigured(
                '{cls} is missing the {op} operation. '
                'Please define the {meth} method'.format(
                    cls=self.__class__.__name__, op=operation_name,
                    meth=self.service_operations[operation_name]))

        try:
            response_node = exec_operation(request, body_node)
        except Exception as e:
            # An error occured when executing the operation. We should return a proper SOAP response
            # but this error should be logged!
            logger.error(
                'soap.error',
                operation=operation_name
            )
            return self.soap_fault_server(str(e))

        return self.render_to_response(self.get_soap_envelope(response_node))

    def render_to_response(self, xml_node):
        """ Given a lxml element, generates a HttpResponse instance and returns it. """
        raw_xml = force_bytes('<?xml version="1.0" encoding="UTF-8"?>') \
            + et.tostring(xml_node, pretty_print=True)
        return HttpResponse(raw_xml, content_type='text/xml')

    def soap_fault_client(self, msg):
        """ Return a SOAP Client Fault with the given message. """
        return self._soap_fault('SOAP-ENV:Client', msg)

    def soap_fault_server(self, msg):
        """ Return a SOAP Client Fault with the given message. """
        return self._soap_fault('SOAP-ENV:Server', msg)

    def _soap_fault(self, code, msg):
        soap_fault = et.Element(self.ns('soap', 'Fault'))
        soap_faultcode = et.SubElement(soap_fault, 'faultcode')
        soap_faultcode.attrib[self.ns('xsi', 'type')] = 'xsd:string'
        soap_faultcode.text = code
        soap_faultstring = et.SubElement(soap_fault, 'faultstring')
        soap_faultstring.attrib[self.ns('xsi', 'type')] = 'xsd:string'
        soap_faultstring.text = msg
        return self.render_to_response(self.get_soap_envelope(soap_fault))
