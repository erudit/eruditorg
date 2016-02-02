import crypt

from django.contrib.auth.backends import ModelBackend
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from erudit.utils.mandragore import get_user_from_mandragore


class MandragoreBackend(ModelBackend):
    """ Authenticate users against the Mandragore database """

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
            return user
