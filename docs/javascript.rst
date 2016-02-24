Développement front-end javascript
==================================

* On utilise du ``DOM-based Routing`` tel que décrit dans http://www.paulirish.com/2009/markup-based-unobtrusive-comprehensive-dom-ready-execution/

Principes
^^^^^^^^^
Lorsqu'une page doit exécuter du javascript custom:

* On place ce javascript dans un fichier qui a le nom de la page
* Ce fichier est placé dans le répertoire propre à l'app de laquelle la page fait partie
* **Décrire brièvement le mécanisme d'abonnement entre le routeur et le controlleur**
* Chaque page identifie le controlleur qui lui est associé en spécifiant un ``data-attribute`` dans le tag ``<body>``

Exemple
^^^^^^^
* **Exemple de code avec dépôt de fichier dans espace utilisateur**

Organisation du code javascript
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Structure des répertoires javascript::

    .
    ├── build
    │   ├── erudit-scripts-dev.js
    │   └── erudit-vendors-dev.js
    │
    ├── controllers
    │   └── public
    │       └── journal
    │           └── article.js
    │   └── userspace
    │       └── editor
    │       └── journal
    └── mains.js


Utilisation de django-pipeline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* On utilise 3 sets
    * ``vendor``: les scripts des tiers;
    * ``public``: les scripts du site public;
    * ``userspace``: les scripts de l'espace utilisateur
