Tableau de bord bibliothèques
=============================

Le tableau de bord bibliothèques permet aux bibliothécaires d'accéder à leurs services.
Certains services sont fournis par ``www.erudit.org`` tandis que d'autres sont fournis par ``retro.erudit.org``.

Import des données
------------------

Les données sont importées depuis ``retro.erudit.org`` avec la commande :py:mod:`core.subscription.management.commands.import_restrictions`.
L'attribut ``legacy_organisation_profile`` contient les informations qui permettent de faire le lien entre la BD ``restriction``
et la BD ``eruditorg``. La commande renseigne le :py:class:`LegacyOrganisationProfile`.


Les restrictions sont importées avec la commande suivante:

::

  python manage.py import_restrictions

Accès au tableau de bord
------------------------

Un utilisateur a accès au tableau de bord bibliothèques si:

1. Il est membre de l':py:class:`Organisation` (la bibliothèque).
2. L'organisation a un abonnement actif.
