import base64

from suds.client import Client


class Victor(object):

    def __init__(self, url, username, password):
        self.client = Client(url)
        self._initialize_session(username, password)

    def _initialize_session(self, username, password):
        """ Retrieve a session token from Victor """
        authorization = base64.encodebytes(
            '{};{}'.format(username, password).encode('utf-8')
        ).decode().replace("\n", "")

        session_token = self.client.service.GetSessionToken(authorization)

        # Use the session token to get an Auth token
        auth_token = base64.encodebytes(
            "{};{}".format(username, session_token).encode('utf-8')
        ).decode().replace("\n", "")

        # Put the auth token in the session token header
        token = self.client.factory.create('SessionToken')
        token.auth_token = auth_token
        self.client.set_options(soapheaders=(token,))

    def get_all_subscribers_with_active_subscriptions(self):
        return self.client.service.GetAllSubscribersWithActiveSubscriptions()

    def get_all_magazines(self):
        return self.client.service.GetAllMagazines()

    def get_subscriber_contact_informations(self, product_name):
        """ Get contact informations for a magazine

        Return all the subscriber contact informations for a given magazine

        Args:
            product_name: the code of the magazine

        """
        return self.client.service.GetSubscriberContactInformations(
            product_name
        )
