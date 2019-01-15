Consultation des articles sur la plateforme
===========================================

La manière dont un article est consulté sur Érudit dépend des attributs des objets :py:class:`~erudit.models.core.Collection` Journal et Issue.

Généralités
^^^^^^^^^^^

Les revues d'Érudit sont dans l'un de ces 4 fonds:

* Érudit
* Centre for Digital Scholarship
* NRC Research Press
* Persée

La manière dont les articles est affichée sur le site dépend du fond duquel l'article fait partie.


Érudit
------

Les articles du fond ``erudit`` sont consultables sur la plateforme Érudit. Ces articles sont produits par Érudit, stockés dans notre dépôt Fedora et indexés dans Solr.

Centre for Digital Scholarship
------------------------------

Les articles du fonds ``unb`` sont produits par le Centre for Digital Scholarship, stockés "en partie" dans notre dépôt Fedora et indexés dans Solr. Les sommaires des numéros sont consultables sur Érudit, mais les articles sont consultables sur les instances OJS des revues.

NRC Research press
------------------

Les articles du fond ``nrc`` sont consultables sur les sites des revues. Ils ne sont pas stockés dans le dépôt Fedora d'Érudit ni indexés dans Solr. On ne fait qu'afficher la liste des revues.

Persée
------

Les articles du fond ``persee`` sont consultables sur la plateforme Persée. Ils ne sont pas stockés dans le dépôt Fedora d'Érudit, mais ils sont indexés dans Solr.

======     ================  ==================  =======
           Liste des revues  Sommaire du numéro  Article
erudit     oui               oui                 oui
unb        oui               oui                 non
nrc        oui               non                 non
persee     oui               non                 non
======     ================  ==================  =======

Ce comportement est défini par les valeurs des attributs des modèles Collection, Journal, Issue et Article.

Comportement défini par des attributs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Collection
----------

L'attribut :py:attr:`~erudit.models.core.Collection.is_main_collection` permet de spécifier si le contenu d'un fonds est hébergé sur Érudit ou non.

.. autoattribute :: erudit.models.core.Collection.is_main_collection
   :noindex:

Si ``is_main_collection`` est à ``True``, Érudit calculera l'embargo pour les revues de ce fonds, et les revues du fonds apparaîtront dans les rapports d'abonnements.

Journal
-------

Le comportement du Journal est configurable par deux variables:

.. autoattribute :: erudit.models.Journal.external_url
   :noindex:

.. autoattribute :: erudit.models.Journal.redirect_to_external_url
   :noindex:

Si on spécifie un ``external_url`` et qu'on définit ``redirect_to_external_url``, le lien de la liste des revues redirigera vers le site externe de la revue. C'est ce qu'on fait pour les fonds Persée et NRC.

Issue
-----

Un ``Issue`` peut spécifier un ``external_url``. Si le ``external_url`` est spécifié, on considère que le numéro est hébergé à l'extérieur. On redirige vers le ``external_url`` à partir de l'à-propos de la revue.

.. autoattribute :: erudit.models.Issue.external_url
   :noindex:

On peut se servir du ``external_url`` dans le cas où un numéro d'une revue qui est normalement hébergée sur érudit (donc dans le fond érudit) est exceptionnelemtn hébergée à l'extérieur de la plateforme.

L'attribut ``is_external`` est utilisé pour déterminer si un ``Issue`` est hébergé sur la plateforme Érudit ou à l'externe.

.. autoattribute :: erudit.models.Issue.is_external
   :noindex:

On se sert de ``is_external`` pour afficher, dans le sommaire du numéro, un avertissement à l'effet que l'utilisateur sera dirigé à l'extérieur du site pour lire l'article.

``is_external`` est mal défini et est à revoir: d'une part, on n'affiche pas le sommaire du numéro pour les numéros qui ont un ``external_url``, et, d'autre part, on ne devrait pas hardcoder le code ``unb``, d'autant plus que l'affichage des revues ``unb`` sera appelé à changer.

Article
-------

La propriété :py:meth:`erudit.models.Article.is_external` indique si un Article est hébergé à l'extérieur.

.. autoattribute :: erudit.models.Article.is_external
   :noindex:

Si l'article est hébergé à l'extérieur, on prends pour acquis que la fiche Solr correspondante aura un URL.
Cet URL sera retournée par la propriété ``url`` de l'article.

.. autoattribute :: erudit.models.Article.url
   :annotation: = test
   :noindex:
