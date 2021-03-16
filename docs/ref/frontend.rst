Développement front-end
=======================

Configuration de npm
---------------------

Installer les dépendances Node au moyen de ``npm`` :

::

    npm install


Compilation des assets
----------------------

La compilation de tous les assets du projet peut être réalisée au moyen de la tâche Gulp ``build``. Il convient de noter que deux modes d'exécution peuvent être utilisés avec la configuration Gulp du projet : production et développement. Par défaut toutes les tâches Gulp sont exécutées en mode "développement".

Ainsi pour lancer la compilation des assets du projet en mode "développement", il faut exécuter la commande suivante :

::

    npm run gulp -- build

Cette commande va construire tous les assets du projet et les placer dans le répertoire ``./erudit/static/build_dev/``. La particularité de ces assets provient du fait qu'ils ne sont pas minifiés afin d'accélérer leur construction. Il faut également noter que le contenu de ``./erudit/static/build_dev/`` n'est pas commité.

En mode "production", tous les assets construits sont minifiés et placés dans le répertoire ``./erudit/static/build/`` (ce dernier est commité). Pour déclencher la construction des assets en mode "production" il faut utiliser la commande suivante :

::

    npm run gulp -- build --production

Cette commande devrait être systématiquement exécutée avant de créer un commit impliquant des modifications des assets.


Live reloading
--------------

Le *live reloading* est fourni par la tâche Gulp ``watch`` :

::

    npm run gulp -- watch

Pour utiliser le *live reload* dans votre browser, utiliser l'extension chrome:

https://chrome.google.com/webstore/detail/livereload/jnihajbhpnppcggbcgedagnkighmdlei

Au besoin, il faudra forwarder le port de la vm-dev:

::

    config.vm.network :forwarded_port, guest: 35729, host: 35729


Hot reloading
-------------

Le *hot reloading* permet de mettre à jour les fichiers JS/CSS spécifiques à l'application Érudit et d'appliquer les changements sans avoir à recharger la page. Pour utiliser le *hot reloading* il est nécessaire d'exécuter au moins une fois la commande de construction des assets en mode "développement" :

::

    npm run gulp -- build

Il est ensuite nécessaire de démarrer un micro serveur chargé de servir les fichiers JS/CSS Érudit et de déclencher les mises à jour des pages au moyen de la tâche ``webpack-dev-server`` :

::

    npm run gulp -- webpack-dev-server

Enfin, il faut ajouter le paramètre suivant au fichier de configuration local ``.env`` :

::

    WEBPACK_DEV_SERVER_URL = 'http://localhost:8080'

Il convient de noter qu'en cas d'utilisation du *hot reloading* le contenu des fichiers CSS construits est placé au sein des applications JS (eg. *PublicApp.js* ou *UserspaceApp.js*) et est dynamiquement injecté dans la page.

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

    // controllers/ArticleDetailController.js

    export default {
      init: function() {
        // The init action is mandatory
        console.log("Article detail");
      },
      other_action: function() {
        // Do something else here
      },
    };

Ce script permet la création d'un contrôleur. L'enregistrement de ce contrôleur peut être réaliser de la façon suivante :

::

    // MyApp.js

    import 'babel-polyfill';

    import DOMRouter from './core/DOMRouter';
    import ArticleDetailController from './controllers/ArticleDetailController';


    // Defines the router and initializes it!
    let router = new DOMRouter({
        'public:journal:article-detail': ArticleDetailController,
    });
    $(document).ready(function(ev) { router.init(); });

Si une page dont la balise ``<body>`` contient un attribut ``data-controller`` - avec pour valeur ``public:journal:article-detail`` - est chargée, alors ce contrôleur sera appellé.

Organisation du code javascript
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Structure des répertoires javascript::

    .
    ├── build
    │   └── [...]
    │   │   ├── erudit-scripts-dev.js
    │   │   └── erudit-vendors-dev.js
    │
    ├── build_dev
    │
    ├── js
    │   ├── controllers
    │   │   └── public
    │   │   │   └── journal
    │   │   │   │   └── ArticleDetailController.js
    │   │   │   │   └── JournalListController.js
    │   │   │   └── HomeController.js
    │   │   │   └── index.js
    │   │   └── userspace
    │   │       └── editor
    │   │       │   └── FormController.js
    │   │       └── index.js
    │   └── core
    │   │   └── DOMRouter.js
    │   └── PublicApp.js
    │   └── UserspaceApp.js
