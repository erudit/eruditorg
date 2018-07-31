import base64

from django.conf import settings
from suds.client import Client


class Victor:
    @staticmethod
    def get_configured_instance():
        assert settings.VICTOR_SOAP_USERNAME and settings.VICTOR_SOAP_PASSWORD
        return Victor(
            settings.VICTOR_SOAP_URL,
            settings.VICTOR_SOAP_USERNAME,
            settings.VICTOR_SOAP_PASSWORD)

    def __init__(self, url, username, password):
        self.client = Client(url)
        self._initialize_session(username, password)

    def _initialize_session(self, username, password):
        """ Retrieve a session token from Victor """
        authorization = base64.encodebytes(
            '{};{}'.format(username, password).encode()
        ).decode().replace("\n", "")

        session_token = self.client.service.GetSessionToken(authorization)

        # Use the session token to get an Auth token
        auth_token = base64.encodebytes(
            "{};{}".format(username, session_token).encode()
        ).decode().replace("\n", "")

        # Put the auth token in the session token header
        token = self.client.factory.create('SessionToken')
        token.auth_token = auth_token
        self.client.set_options(soapheaders=(token,))

    def get_subscriber_contact_informations(self, product_name):
        result = self.client.service.GetSubscriberContactInformations(product_name)
        try:
            return result.SubscriberContactInformation
        except AttributeError:
            return []
