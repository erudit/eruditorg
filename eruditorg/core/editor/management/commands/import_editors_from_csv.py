import csv
import logging

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import Q

from erudit.models import Journal
from core.accounts.utils import generate_unique_username
from core.authorization.defaults import AuthorizationConfig
from core.authorization.models import Authorization

logger = logging.getLogger(__name__)
authorization_codename = AuthorizationConfig.can_manage_issuesubmission.codename
User = get_user_model()


class Command(BaseCommand):
    """ Import restrictions from the restriction database """
    help = 'Import editors from a csv file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path', action='store', dest='path',
            help="id of the organisation to import"
        )

        parser.add_argument(
            '--report', action='store_true', dest='report',
        )

    def produce_report(self):
        """ Produce the editor report """

        authorizations = Authorization.objects.filter(
            authorization_codename="editor:can_manage_issuesubmission"
        ).order_by("user")

        for authorization in authorizations:
            if authorization.content_object:
                print("{username},{email},{shortname},{will_receive_email}".format(
                    username=authorization.user.username,
                    email=authorization.user.email,
                    shortname=authorization.content_object.code,
                    will_receive_email=True if authorization.user.password.startswith('!') else False
                ))

    def handle(self, *args, **options):

        if options.get('report', False):
            self.produce_report()
            return

        self.path = options.get('path', None)
        journal_content_type = ContentType.objects.get_for_model(Journal)
        with open(self.path, 'r') as editor_file:
            reader = csv.reader(editor_file)
            for row in reader:
                row = [cell.strip() for cell in row]
                shortname, journal_name, fullname, email = row[0:4]

                try:
                    journal = Journal.legacy_objects.get_by_id(shortname)
                except Journal.DoesNotExist:
                    logger.error('Journal {} does not exist'.format(
                        shortname
                    ))
                    continue

                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    username = generate_unique_username(fullname)
                    user = User(username=username, email=email)
                    user.set_unusable_password()
                    user.save()

                journal.members.add(user)

                auth, created = Authorization.objects.get_or_create(
                    user=user,
                    authorization_codename=authorization_codename,
                    object_id=journal.pk,
                    content_type=journal_content_type
                )

                if created:
                    logger.info(
                        "Authorization: {}, {}, {}, CREATED".format(
                            user,
                            journal,
                            authorization_codename
                        )
                    )
                else:
                    logger.info(
                        "Authorization: {}, {}, {}, UPDATED".format(
                            user,
                            journal,
                            authorization_codename
                        )
                    )
