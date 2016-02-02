import logging

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from erudit.models import Publisher

from erudit.utils.mandragore import (
    fetch_accounts_from_mandragore,
    fetch_users_from_edinum,
    fetch_series_from_edinum,
    can_create_mandragore_user,
    create_or_update_mandragore_user,
    user_coherent_with_mandragore,
    MandragoreError
)

log = logging.getLogger(__name__)


class Command(BaseCommand):

    help = """Import publisher accounts from a csv file"""

    def handle(self, *args, **options):

        self.created_or_updated_publishers = []
        self.created_or_updated_journals = []

        persons_to_add = {}

        # The data required to create the user accounts is in Edinum
        # and Mandragore.
        #
        # We need to manually join between the databases, so we keep
        # local association tables for this.
        person_ids_to_fetch = set()
        persons_collections = {}
        collections_editor = {}

        # Retrieve the accounts from Mandragore
        for (username, email, person_id,
             collectionid) in fetch_accounts_from_mandragore():

            user = User.objects.filter(username=username)
            if user.exists():
                user = user.first()
                user_coherent, message = user_coherent_with_mandragore(
                    user, {
                        'username': username,
                        'person_id': person_id
                    }
                )
                if not user_coherent:
                    raise MandragoreError(
                        "Error importing user {}: {}".format(username, message)  # noqa
                    )

            if can_create_mandragore_user(username, person_id):
                person_ids_to_fetch.add(person_id)
                persons_collections[person_id] = collectionid

                user = create_or_update_mandragore_user(
                    person_id, email=email, username=username
                )

                persons_to_add[person_id] = user

        # Update the accounts with the values from Edinum
        for (person_id, firstname,
             middlename, familyname) in fetch_users_from_edinum(
                 person_ids_to_fetch):
            user = persons_to_add[person_id]

            create_or_update_mandragore_user(
                person_id, email=email, username=user.username,
                first_name=firstname, last_name=familyname
            )

        # Add the users to the publisher
        for (id, editor_id) in fetch_series_from_edinum(persons_collections.values()):
            collections_editor[id] = editor_id

        for person_id, collection in persons_collections.items():
            try:
                publisher_id = collections_editor[collection]
                publisher = Publisher.objects.get(edinum_id=publisher_id)
                to_add = persons_to_add[person_id]
                to_add.save()

                publisher.members.add(to_add)
                publisher.save()
            except Exception as e:
                log.error(
                    e
                )
