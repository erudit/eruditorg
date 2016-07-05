# -*- coding: utf-8 -*-

import base64
import hashlib

from django.conf import settings
from django.contrib.auth.hashers import PBKDF2PasswordHasher


class PBKDF2WrappedAbonnementsSHA1PasswordHasher(PBKDF2PasswordHasher):
    algorithm = 'pbkdf2_wrapped_abonnements_sha1'

    def encode_sha1_hash(self, sha1_hash, salt, iterations=None):
        return super(PBKDF2WrappedAbonnementsSHA1PasswordHasher, self).encode(
            sha1_hash, salt, iterations)

    def encode(self, password, salt, iterations=None, legacy_salt=None):
        """ Encode using the crypt function from the legacy system. """
        sha1_hash = self.sha1(password, legacy_salt)
        return self.encode_sha1_hash(sha1_hash, salt, iterations)

    def sha1(self, password, legacy_salt=None):
        """ Encode using the crypt function from the legacy system. """
        if legacy_salt is None:
            legacy_salt = settings.INDIVIDUAL_SUBSCRIPTION_SALT
        to_sha = password.encode('utf-8') + legacy_salt.encode('utf-8')
        hashy = hashlib.sha1(to_sha).digest()
        sha1_hash = base64.b64encode(hashy + legacy_salt.encode('utf-8')).decode('utf-8')
        return sha1_hash
