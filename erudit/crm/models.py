from django.db import models
from erudit import models as e


class Organisation(models.Model):
    """Organisation"""

    # identification
    name
    parent
    type

    # coordinates
    email
    tel
    fax
    url
    address

class OrganisationType(models.Model):

    name

class Person(models.Model):
    """Personne"""

    # identification
    salutation?
    lastname
    firstname
    display_name

    # coordinates
    email
    address

class PersonRole(models.Model):
    """Rôle"""

    name
    for_journal

class JournalPersonRole(models.Model):
    """Rôle pour revue"""

    # identification
    journal
    person
    role

    # meta
    date_start
    date_end
    comment
