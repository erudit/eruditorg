Permissions
===========

Principes
---------

Les permissions de l'application Érudit sont définies via l'utilisation de *django-rules*. Une permission est ainsi définie par un ensemble de prédicats. Chaque prédicat effectue une vérification simple telle que :

* vérifier que l'utilisateur soit un super-utilisateur
* vérifier qu'il soit le propriétaire d'une revue
* ...

Certaines permissions peuvent nécessiter la vérification d'une **autorisation**. Est-ce que l'utilisateur a bien l'autorisation d'ajouter un nouveau numéro ? Est-ce que l'utilisateur a l'autorisation d'attribuer lui-même des autorisations à d'autres utilisateurs ? Ces autorisations sont définies par les instances du modèle ``core.authorization.models.Authorization``.

Ainsi certaines permissions, telle que définies par l'utilisation de *django-rules*, sont basées sur la vérification d'un prédicat impliquant de s'assurer que l'utilisateur en question a bien l'autorisation de réaliser telle ou telle action.

Définition des autorisations
----------------------------

 .. automodule :: core.authorization.defaults
    :members:
