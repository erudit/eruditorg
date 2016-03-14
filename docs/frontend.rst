Développement front-end
=======================

Configuration de Gulp
---------------------

1. Installer le paquet NPM

::

    sudo npm install --save-dev


2. Configurer l'environnement Gulp

À partir du fichier fourni dans le dépôt

::

    cp ./tools/static/.env.json.sample ./tools/static/.env.json


3. Démarrer Gulp

::

    ./node_modules/.bin/gulp --gulpfile ./tools/static/gulpfile.js watch


4. Configurer le live reload

Pour utiliser le *live reload* dans votre browser, utiliser l'extension chrome:

https://chrome.google.com/webstore/detail/livereload/jnihajbhpnppcggbcgedagnkighmdlei

Au besoin, il faudra forwarder le port de la vm-dev:

::

    config.vm.network :forwarded_port, guest: 35729, host: 35729


Développement front-end javascript
----------------------------------

* On utilise du ``DOM-based Routing`` tel que décrit dans http://www.paulirish.com/2009/markup-based-unobtrusive-comprehensive-dom-ready-execution/

Principes
^^^^^^^^^

* Chaque page faisant intervenir un script Javascript doit être associé à un unique fichier Javascript.
* Ce fichier doit être placé dans le répertoire propre à l'application correspondant à la page considérée (dans ``static/scripts/controllers/``)

Chaque script associé à une page obéit à une notion de "Contrôleur". Ce contrôleur doit être enregistré auprès
d'un "Routeur" dont la fonction est de déterminer le contrôleur à exécuter en fonction de la page affichée.

Concrètement ce routeur inspecte le contenu de la balise ``<body>`` et recherche la présence de deux *data-attributes* :

* ``data-controller`` : la valeur de cet attribut sert à définir le contrôleur qui sera exécuté
* ``data-action``: la valeur de cet attribut sert à définir une action spécifique du contrôleur en question à exécuter. L'utilisation de ``data-action`` n'est pas obligatoire

Pour chaque contrôleur une action ``init`` est obligatoire et est systématiquement exécutée au chargement de la page, quelle que soit la valeur de l'attribut ``data-action``.

Exemple
^^^^^^^

Voici un exemple de contrôleur associé à la vue détail d'un article :

::

    ROUTER.registerController('public:journal:article-detail', {
      init: function() {
        // The init action is mandatory
        console.log("Article detail");
      },
      other_action: function() {
        // Do something else here
      },
    });

Ce script permet la création d'un contrôleur et l'enregistrement de celui-ci auprès du routeur global. Si une page dont la balise ``<body>`` contient un attribut ``data-controller`` - avec pour valeur ``public:journal:article-detail`` - est chargée, alors ce contrôleur sera appellé.

Organisation du code javascript
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Structure des répertoires javascript::

    .
    ├── js
    │   ├── build
    │   │   ├── erudit-scripts-dev.js
    │   │   └── erudit-vendors-dev.js
    │
    ├── scripts
    │   ├── controllers
    │   │   └── public
    │   │       └── journal
    │   │           └── articleDetail.js
    │   │   └── userspace
    │   │       └── editor
    │   │           └── [...]
    │   │       └── journal
    │   │           └── [...]
    │   └── mains.js


Utilisation de django-pipeline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* On utilise 3 sets
    * ``vendor``: les scripts des tiers;
    * ``public``: les scripts du site public;
    * ``userspace``: les scripts de l'espace utilisateur
