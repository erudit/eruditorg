from datetime import datetime

import pymysql

from django.contrib.auth.models import User
from django.conf import settings

from erudit.models import MandragoreProfile


class MandragoreError(Exception):
    pass


def create_mandragore_profile_for_user(person_id, user):
    """ Create a mandragore profile for this person """
    mandragoreprofile = MandragoreProfile()
    mandragoreprofile.mandragore_id = person_id
    mandragoreprofile.synced_with_mandragore = True
    mandragoreprofile.user = user
    mandragoreprofile.sync_date = datetime.now()
    mandragoreprofile.save()
    return mandragoreprofile


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

    conn = pymysql.connect(
        host=mandragore['HOST'],
        unix_socket='/tmp/mysql.sock',
        user=mandragore['USER'],
        passwd=mandragore['PASSWORD'],
        db=mandragore['NAME'],
    )

    cur = conn.cursor()
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
    EDINUM_SERIE_QUERY = """SELECT s.ID, ap.PersonId from Series s, contributionseries cs, contribution c, artificialperson ap WHERE
s.ID = cs.SeriesID AND
cs.ContributionID = c.ID AND
c.PersonID = ap.PersonID AND
c.ContributiontypeID = '3' AND
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

    if MandragoreProfile.objects.filter(mandragore_id=person_id).exists():
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

     Raise MandragoreException when any of these conditions is not met. """

    user = User.objects.get(username=username)

    if not hasattr(user, "mandragoreprofile"):
        raise MandragoreError(
            "The user does not have a Mandragore profile"
        )

    if user.mandragoreprofile.mandragore_id != str(person_id):
        raise MandragoreError(
            "Mandragore id mismatch. Expected: {}, Actual: {}".format(
                person_id,
                user.mandragoreprofile.mandragore_id
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

    if user.mandragoreprofile.mandragore_id != str(mandragore_values['person_id']):  # noqa
        return False, "Person_id mismatch: {} != {}".format(
            user.mandragoreprofile.mandragore_id,
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
    conn = pymysql.connect(
        host=host,
        unix_socket='/tmp/mysql.sock',
        user=user,
        passwd=passwd,
        db=db,
    )

    cur = conn.cursor()
    cur.execute(query)
    results = cur.fetchall()
    conn.close()
    return results
