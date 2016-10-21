Internationalisation
====================

Configuration du poste du développeur
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Dans le répertoire home de l'utilisateur, créer un fichier ``.transifexrc`` qui contient les informations du compte utilisateur:

  ::

    [https://www.transifex.com]
    hostname = https://www.transifex.com
    username = username
    password = password
    token =

Installer le client transifex dans le virtualenv du projet:

  ::

    pip install transifex-client

Mise à jour des sources
^^^^^^^^^^^^^^^^^^^^^^^

  ::

    tx push -s

Mise à jour des traductions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

  ::

    tx pull -l en
    python eruditorg/manage.py compilemessages
