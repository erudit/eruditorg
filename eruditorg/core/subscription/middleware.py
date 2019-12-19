import redis
import structlog

from base64 import urlsafe_b64decode
from binascii import unhexlify
from Crypto.Cipher import AES
from datetime import datetime
from ipaddress import ip_address, ip_network
from ipware import get_client_ip
from typing import Union
from urllib.parse import unquote

from .models import JournalAccessSubscription
from core.subscription.models import UserSubscriptions
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

logger = structlog.getLogger(__name__)


class SubscriptionMiddleware(MiddlewareMixin):
    """ This middleware attaches subscription information to the request object.

    This middleware attaches informations related to the subscription
    of the current user to the request object.
    """

    def _get_user_referer_for_subscription(self, request):
        """ Return the referer of the user, with regards to subscription validation

        If the user has a referer set in her session, return this referer. Otherwise
        return the value of 'HTTP_REFERER'
        """
        referer = request.COOKIES.get('HTTP_REFERER') or request.session.get('HTTP_REFERER')
        return referer if referer else request.META.get('HTTP_REFERER')

    def _get_user_ip_address(self, request):
        if request.user.is_active and request.user.is_staff and 'HTTP_CLIENT_IP' in request.META:
            return request.META.get('HTTP_CLIENT_IP', None)
        user_ip, _ = get_client_ip(request, proxy_order='right-most')
        return user_ip

    def process_request(self, request):
        # Tries to determine if the user's IP address is contained into
        # an institutional IP address range.

        ip = self._get_user_ip_address(request)
        if request.user.is_active and request.user.is_staff:
            ip = request.META.get('HTTP_CLIENT_IP', ip)

        request.subscriptions = UserSubscriptions()
        subscription = JournalAccessSubscription.\
            valid_objects.institutional().get_for_ip_address(ip)\
            .select_related('organisation').first()
        if subscription:
            request.subscriptions.add_subscription(subscription)

        # Tries to determine if the subscriber is refered by a subscribed organisation
        referer = self._get_user_referer_for_subscription(request)
        subscription = JournalAccessSubscription.\
            valid_objects.institutional().get_for_referer(referer)
        if subscription:
            request.subscriptions.add_subscription(subscription)
            request.session['HTTP_REFERER'] = referer

        # Tries to determine if the user has an individual account
        if request.user.is_authenticated:
            for subscription in JournalAccessSubscription.valid_objects.individual().select_related(
                'sponsor', 'organisation'
            ).filter(user=request.user):
                request.subscriptions.add_subscription(subscription)

        casa_key = getattr(settings, 'GOOGLE_CASA_KEY', None)
        casa_token = request.GET.get('casa_token', None)
        user_ip = self._get_user_ip_address(request)
        if casa_key and casa_token and user_ip:
            subscription_id = self.casa_authorize(casa_key, casa_token, user_ip)
            try:
                subscription = JournalAccessSubscription.valid_objects.get(pk=subscription_id)
                request.subscriptions.add_subscription(subscription)
            except JournalAccessSubscription.DoesNotExist:
                pass

    def casa_authorize(self, key: str, token: str, user_ip: str) -> Union[str, bool]:
        """
        Check if the user is authorized to see the full text article.

        :param key: the encryption key
        :param token: the CASA token
        :param user_ip: the IP address of the user

        :returns: The subscription ID if the user is authorized, False otherwise.
        """
        # The key needs to be converted from the 32-byte hex-encoded form to a 16-byte binary string
        # before use.
        key = unhexlify(key)

        # The CASA token consists of two components separated by a colon:
        # * A 12-byte unique random number (nonce).
        # * A variable length payload which includes a 16-byte signature.
        components = token.split(':')
        if len(components) != 2:
            # Badly formed token.
            logger.info(
                'CASA',
                msg='Badly formed token.',
                token=token,
                user_ip=user_ip,
            )
            return False

        # The CASA token components are encoded using Base-64 encoding suitable for URLs. They need
        # to be decoded before use. Since the payload is of variable length, it needs some padding.
        nonce = urlsafe_b64decode(components[0])
        payload = urlsafe_b64decode(components[1] + '=' * (4 - len(components[1]) % 4))

        # Decrypt and verify the payload.
        try:
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            # The payload includes a 16-byte signature at the end used for the verify.
            data = cipher.decrypt_and_verify(payload[:-16], payload[-16:])
        except ValueError:
            # Either the message has been modified or it didn’t come from Google Scholar.
            logger.info(
                'CASA',
                msg='Decryption failed.',
                token=token,
                user_ip=user_ip,
            )
            return False

        # Allow up to three times to handle user clicking on a search result a few times
        # (e.g., comparing figures in a few papers etc).
        if self._nonce_count(nonce) > 3:
            logger.info(
                'CASA',
                msg='Token used more than 3 times.',
                token=token,
                user_ip=user_ip,
            )
            return False

        fields = data.decode().split(':')
        if len(fields) < 3:
            # Badly formatted payload.
            logger.info(
                'CASA',
                msg='Badly formed payload.',
                token=token,
                user_ip=user_ip,
            )
            return False

        # The timestamp in the token is the number of microseconds since Unix Epoch.
        timestamp = fields[0]
        if int(datetime.now().timestamp() * 1e6) - int(timestamp) > 60 * 60 * 1e6:
            # Token is too old and is no longer valid.
            logger.info(
                'CASA',
                msg='Token is older than 1 hour.',
                time_now=datetime.now().isoformat(),
                time_token=datetime.fromtimestamp(int(timestamp) / 1e6).isoformat(),
                token=token,
                user_ip=user_ip,
            )
            return False

        # The ip_subnet field is URL-escaped in the token. It needs to be unescaped before use.
        ip_subnet = unquote(fields[2])
        if ip_address(user_ip) not in ip_network(ip_subnet):
            # User IP is outside the IP subnet the token is valid for.
            logger.info(
                'CASA',
                msg='IP address not in subnet.',
                ip_subnet=ip_subnet,
                token=token,
                user_ip=user_ip,
            )
            return False

        # The subscriber_id field is URL-escaped in the token. It needs to be unescaped before use.
        subscriber_id = unquote(fields[1])
        logger.info(
            'CASA',
            msg='Successful authorization.',
            subscriber_id=subscriber_id,
            token=token,
            user_ip=user_ip,
        )

        return subscriber_id

    def _nonce_count(self, nonce: str) -> int:
        """
        Check the nuber of times a nonce has been seen.

        :param nonce: the nonce

        :returns: The number of times the nonce has been seen.
        """
        try:
            # Try to store in Redis the number of times a particular nonce has been seen.
            redis_host = getattr(settings, 'REDIS_HOST')
            redis_port = getattr(settings, 'REDIS_PORT')
            redis_index = getattr(settings, 'REDIS_INDEX')
            if not redis_host or not redis_port or not redis_index:
                raise redis.exceptions.ConnectionError
            r = redis.Redis(host=redis_host, port=redis_port, db=redis_index)
            key = 'google_casa_nonce_{}'.format(nonce)
            count = r.get(key)
            count = int(count) + 1 if count is not None else 1
            r.set(key, count, 3600)
            return count
        except redis.exceptions.ConnectionError:
            # No access to Redis so we have no way to know how many times this nonce has been seen.
            return 0
