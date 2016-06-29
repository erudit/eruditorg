Dépôt de fichiers
=================

Configurer les équipes de production
------------------------------------

Cette section décrit les étapes pour configurer les équipes de production dans l'interface d'administration de Django.

Créer les utilisateurs
^^^^^^^^^^^^^^^^^^^^^^

Créer un utilisateur Django par membre d'une équipe de production.

Créer les groupes
^^^^^^^^^^^^^^^^^

Créer un groupe Django par chaque équipe de production.

Créer des équipes de production
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Créer un :py:class:`~core.editor.models.ProductionTeam` par équipe de production.
Associer le groupe au :py:class:`~core.editor.models.ProductionTeam` correspondant.
Associer les revues au :py:class:`~core.editor.models.ProductionTeam` qui les produit.

Donner les permissions à l'équipe de production
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pour pouvoir valider des numéros, l'équipe de production doit avoir l'autorisation « Valider les numéros »

Cette autorisation s'assigne dans la page de gestion des `autorisations`_.

Pour chaque groupe de production:
    * Créer un objet autorisation
    * Groupe: choisir le groupe associé à l'équipe de production
    * Autorisation: choisir `Valider les numéros`

Cette autorisation n'a pas de cible particulière: le groupe peut valider les dépôts de fichiers pour toutes les revues.

.. _autorisations: http://preprod.erudit.org/fr/admin/authorization/authorization/

