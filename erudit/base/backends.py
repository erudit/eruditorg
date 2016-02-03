import types
import crypt

from django.contrib.auth.backends import ModelBackend
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from erudit.utils.mandragore import (
    get_user_from_mandragore,
    update_user_password
)


def set_password_mandragore(self, raw_password):
    """ Set the password in the Mandragore database
    """

    # Use only 8 characters in the salt. Otherwise the generated hash will be
    # to long for the mandragore MotDePasse Field.
    the_hash = crypt.crypt(
        raw_password,
        salt=crypt.mksalt(
            method=crypt.METHOD_SHA512
        )[:11]
    )

    update_user_password(self.username, the_hash)
    self.save()


class MandragoreBackend(ModelBackend):
    """ Authenticate users against the Mandragore database

    Monkeypatches django.contrib.auth.models.User to replace `set_password` with
    :py:func:`set_password_mandragore`
    """

    def authenticate(self, username=None, password=None):

        User = get_user_model()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise PermissionDenied()

        # Being connected to the "Mandragore" database is not
        # mandatory. Thus we do not raise `PermissionDenied` but
        # let Django try to authenticate the user with the ModelBackend.
        if ((not hasattr(settings, 'EXTERNAL_DATABASES') or
             type(settings.EXTERNAL_DATABASES) != dict or
             'mandragore' not in settings.EXTERNAL_DATABASES)):
            return None

        mand_user, mand_pw = get_user_from_mandragore(username)

        _, algo, salt, hashed_pass = mand_pw.split('$')

        user_pass = crypt.crypt(
            password, '${}${}'.format(
                algo,
                salt,
            )
        )

        if user_pass == mand_pw:
            user.set_password = types.MethodType(set_password_mandragore, user)
            return user
