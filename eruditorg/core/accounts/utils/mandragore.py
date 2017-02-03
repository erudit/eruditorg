# -*- coding: utf-8 -*-

from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User

from ..models import LegacyAccountProfile
from .pymysql import pymysql_connection


class MandragoreError(Exception):
    pass


def create_mandragore_profile_for_user(person_id, user):
    """ Create a mandragore profile for this person """
    mandragoreprofile = LegacyAccountProfile()
    mandragoreprofile.origin = LegacyAccountProfile.DB_MANDRAGORE
    mandragoreprofile.legacy_id = person_id
    mandragoreprofile.synced_with_origin = True
    mandragoreprofile.user = user
    mandragoreprofile.sync_date = datetime.now()
    mandragoreprofile.save()
    return mandragoreprofile


def update_user_password(username, the_hash):
    """ Update the password of the user in mandragore """
    MANDRAGORE_UPDATE_QUERY = """
    UPDATE CompteUtilisateur set MotDePasse="{}" WHERE NomUtilisateur="{}"
    """
    mandragore = settings.EXTERNAL_DATABASES['mandragore']

    with pymysql_connection(
        host=mandragore['HOST'],
        username=mandragore['USER'],
        password=mandragore['PASSWORD'],
        database=mandragore['NAME']
    ) as cur:
        cur.execute(MANDRAGORE_UPDATE_QUERY.format(
            the_hash,
            username
        ))


def get_journal_shortname_from_seriesid(seriesid):
    QUERY = """
    SELECT sp.shortname from seriesproduction sp, series s, title t where sp.seriesid=s.id and t.seriesid = s.id and t.id="{}"  # noqa
    """
    edinum = settings.EXTERNAL_DATABASES['edinum']

    with pymysql_connection(
        host=edinum['HOST'],
        username=edinum['USER'],
        password=edinum['PASSWORD'],
        database=edinum['NAME']
    ) as cur:
        cur.execute(QUERY.format(seriesid))
        users = cur.fetchall()
        return users[0]


def get_user_from_mandragore(username):
    MANDRAGORE_USER_QUERY = """
    SELECT NomUtilisateur, MotDePasse FROM CompteUtilisateur WHERE NomUtilisateur="{}"
    """

    mandragore = settings.EXTERNAL_DATABASES['mandragore']

    with pymysql_connection(
        host=mandragore['HOST'],
        username=mandragore['USER'],
        password=mandragore['PASSWORD'],
        database=mandragore['NAME']
    ) as cur:
        cur.execute(MANDRAGORE_USER_QUERY.format(username))
        users = cur.fetchall()
        return users[0]


def fetch_accounts_from_mandragore():

    MANDRAGORE_ACCOUNT_QUERY = """
    SELECT cu.NomUtilisateur, pc.Adresse, cu.PersonneId, cft.CollectionID FROM
    CompteUtilisateur cu,
    PersonneCourriel pc,
    CompteUtilisateurCollectionFluxTravaux cucft,
    CollectionFluxTravaux cft WHERE
    cucft.NomUtilisateur = cu.NomUtilisateur AND
    pc.PersonneID = cu.PersonneId AND
    cucft.CollectionFluxTravauxID = cft.ID;
    """

    mandragore = settings.EXTERNAL_DATABASES['mandragore']

    with pymysql_connection(
        host=mandragore['HOST'],
        username=mandragore['USER'],
        password=mandragore['PASSWORD'],
        database=mandragore['NAME']
    ) as cur:
        cur.execute(MANDRAGORE_ACCOUNT_QUERY)
        return cur.fetchall()


def fetch_users_from_edinum(person_ids_to_fetch):
    EDINUM_PERSON_QUERY = """SELECT pn.ID, pn.FirstName, pn.MiddleName, pn.FamilyName FROM
personname pn WHERE pn.ID in (%s);"""

    if not person_ids_to_fetch:
        return []

    edinum = settings.EXTERNAL_DATABASES['edinum']
    query = EDINUM_PERSON_QUERY % get_list_as_sql(person_ids_to_fetch)

    return open_connection_and_fetchall(
        host=edinum['HOST'],
        user=edinum['USER'],
        passwd=edinum['PASSWORD'],
        db=edinum['NAME'],
        query=query
    )


def fetch_series_from_edinum(series_ids_to_fetch):
    EDINUM_SERIE_QUERY = """SELECT s.ID, t.id from series s, title t WHERE
s.ID = t.SeriesID AND
s.ID IN (%s);"""  # noqa

    if not series_ids_to_fetch:
        return []

    query = EDINUM_SERIE_QUERY % get_list_as_sql(series_ids_to_fetch)
    edinum = settings.EXTERNAL_DATABASES['edinum']
    return open_connection_and_fetchall(
        host=edinum['HOST'],
        user=edinum['USER'],
        passwd=edinum['PASSWORD'],
        db=edinum['NAME'],
        query=query
    )


def can_create_mandragore_user(username, person_id):
    """ Test if we can create this user

    We can only create the user if the following two conditions are met:

    1. There is no user with this username
    2. There is no user with a MandragoreProfile for this person_id"""

    if User.objects.filter(username=username).exists():
        return False

    if LegacyAccountProfile.objects.filter(
            origin=LegacyAccountProfile.DB_MANDRAGORE, legacy_id=person_id).exists():
        return False

    return True


def create_or_update_mandragore_user(person_id, **kwargs):
    """ Create or update a user with a mandragore profile

    Arguments:
      person_id: the mandragore person_id
      the kwargs will be passed to user
    """

    if 'username' not in kwargs:
        raise ValueError

    if can_create_mandragore_user(kwargs['username'], person_id):
        new_user = User(**kwargs)
        new_user.save()
        create_mandragore_profile_for_user(person_id, new_user)
        return new_user

    # Otherwise update the user
    user = get_mandragore_user(kwargs['username'], person_id)
    for key, value in kwargs.items():
        setattr(user, key, value)
    user.save()
    return user


def get_mandragore_user(username, person_id=None, additional_values=None):
    """ Return the user associated with this username

    Make sanity checks to be sure that the user is properly
    associated with the mandragore user id.

    Test that:
        * The user has a Mandragore profile
        * If person_id is specified, that this user is linked to the
          proper Mandragore profile

     Raise MandragoreError when any of these conditions is not met. """

    user = User.objects.get(username=username)

    try:
        mandragoreprofile = LegacyAccountProfile.objects \
            .filter(origin=LegacyAccountProfile.DB_MANDRAGORE).get(user=user)
    except LegacyAccountProfile.DoesNotExist:
        raise MandragoreError(
            "The user does not have a Mandragore profile"
        )

    if mandragoreprofile.legacy_id != str(person_id):
        raise MandragoreError(
            "Mandragore id mismatch. Expected: {}, Actual: {}".format(
                person_id,
                mandragoreprofile.legacy_id
            )
        )

    return user


def user_coherent_with_mandragore(user, mandragore_values):
    """ Check that the user is coherent with the values from mandragore
    """

    if user.username != mandragore_values['username']:
        return False, "Username mismatch: {} != {}".format(
            user.username, mandragore_values['username']
        )

    mandragoreprofile = LegacyAccountProfile.objects \
        .filter(origin=LegacyAccountProfile.DB_MANDRAGORE).get(user=user)

    if mandragoreprofile.legacy_id != str(mandragore_values['person_id']):  # noqa
        return False, "Person_id mismatch: {} != {}".format(
            mandragoreprofile.legacy_id,
            mandragore_values['person_id']
        )

    if 'email' in mandragore_values and user.email != mandragore_values['email']:
        return False, "Email mismatch: {} != {}".format(
            user.email, mandragore_values['email']
        )

    return True, None


def get_list_as_sql(item_list):
    """ Get a string of the list in a format suitable for insertion in a WHERE IN clause """  # noqa
    return ','.join(map(lambda x: '"{}"'.format(str(x)), item_list))


def open_connection_and_fetchall(
        host=None, user=None, passwd=None, db=None, query=None):

    with pymysql_connection(host=host, username=user, password=passwd, database=db) as cur:
        cur.execute(query)
        results = cur.fetchall()
        return results
