import structlog

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

logger = structlog.getLogger(__name__)


class EmailBackend(ModelBackend):
    """Allows a user to login using his e-mail address or his username.

    This backend should be used instead of the builtin `django.contrib.auth.backends.ModelBackend`
    authentication backend.
    """

    def _get_user(self, email_or_username):
        UserModel = get_user_model()

        # Tries to fetch the user instance using the e-mail address or the username
        try:
            try:
                validate_email(email_or_username)
                user = UserModel.objects.get(email=email_or_username.lower())
            except UserModel.MultipleObjectsReturned:
                logger.warning(
                    "login.error", msg="Multiple users with e-mail address", email=email_or_username
                )
                raise UserModel.DoesNotExist
            except ValidationError:
                user = UserModel.objects.get(username=email_or_username)
        except UserModel.DoesNotExist:
            return

        return user

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = self._get_user(username)
        if user and user.check_password(password):
            return user
