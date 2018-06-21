Aperçu du modèle de données
===========================

Cette section décrit les liens entre Fedora Commons, Solr, Django, eulfedora et liberuditarticle.

Résumé
------

* La grande majorité des informations traitées par eruditorg provient de systèmes externes;
* Les classes `Journal`, `Issue` et `Article` décrivent les objets stockés dans Fedora Commons;
* Les articles et revues sont stockées dans Fedora Commons;
* Django utilise eulfedora pour récupérer les objets Fedora Commons;
* liberuditarticle est utilisé pour parser le contenu des articles;
* Les documents Solr sont une indexation des objets Fedora Commons.

Autorité des données
--------------------

eruditorg est un portail donnant accès à des données fournies en grand majorité par des systèmes
externes et fait autorité sur très peu de ces données. Liste des données pour lesquelles eruditorg
fait présentement autorité:

* Abonnements individuels
* Whitelisting pour embargo de numéros
* Profiles de revues (à propos, etc)
* Citations sauvegardées

La liste des revues est aussi maintenue en partie manuellement (les revues OAI sont importées, mais
pas les revues fedora) dans l'admin Django mais ne fait pas autorité sur d'autres systèmes.

Modèles Django
--------------

Les trois modèles suivants sont utilisés pour récupérer les données des articles scientifiques:

* :py:class:`Journal <erudit.models.core.Journal>` (une revue, scientifique ou savante)
* :py:class:`Issue <erudit.models.core.Issue>` (une publication de cette revue)
* :py:class:`Article <erudit.models.core.Article>`

Le modèle suivant est utilisé pour récupérer les données des Thèses:

* :py:class:`Thesis <erudit.models.core.Thesis>`

Modèles hybrides
----------------

Initialement, le système était entièrement basé sur la synchronisation régulière de la BD django
avec les systèmes externes. Une telle synchronisation vient avec pleins de petits problèmes au
niveau de la cohérence des données qui finissent par devenir une montagne.

Depuis un certain temps, on se désengage de cette voie pour s'appuyer directement sur Solr et Fedora
lors du rendering de vues. Il y a donc un effort de "dé-django-isation" en cours qui mènera à terme
à des modèles ``Article`` et ``Issue`` qui ne réfèrent à aucune table de la BD django mais seulement
à un ``localidentifier`` qui permet d'aller chercher les données pertinentes dans Solr et Fedora.
C'est au niveau du modèle lui-même qu'il y a la logique à savoir si telle ou telle information à
propos d'un article ou numéro doit provenir de Fedora, Solr ou (temporairement, le temps de la
migration) la BD django.

Idéalement, pour des raisons de performances, on voudra aller chercher le plus d'informations
possible dans Solr et utiliser Fedora seulement quand c'est nécessaire, mais pour l'instant, dans
chaque vue qui fait référence à un article, on doit charger un `erudit_object` (ce qui a un coût
important). À ce moment, toutes les vues qui impliquent un numéro ou un article doivent charger
un ``erudit_object``. Avec le temps, on voudra s'appuyer de plus en plus sur Solr pour réduire le
nombre de ces vues.

Récupération des données dans Fedora
------------------------------------

Les modèles Django implémentent le :py:class:`FedoraMixin <erudit.fedora.modelmixins.FedoraMixin>`.
Le mixin implémente une méthode ``get_full_identifier()`` qui retourne l'identifiant qui permet de récupérer l'objet dans Fedora.
:py:class:`~erudit.fedora.modelmixins.FedoraMixin` utilise la librairie `eulfedora`_. pour se connecter à ``Fedora``
et retourne un objet d'un type défini dans le module :py:mod:`erudit.fedora.objects`
Chaque type d'objet contenu dans Fedora présente des particularités.
Le module :py:mod:`objects <erudit.fedora.objects>` permet de faire abstraction de ces particularités.

Par exemple, on peut accéder à la page couverture d'un numéro avec le code suivant::

    issue.get_fedora_object().coverpage


.. _eulfedora: https://www.github.com/emory-libraries/eulfedora

Cache des objets Fedora
-----------------------

Ouvrir les articles, publication et sommaires Fedora et les charger dans un objet
``liberuditarticle`` est couteux. Avant la "dé-django-isation" des modèles, ce cout était mitigé par
une cache au niveau des templates, mais depuis qu'on se base de plus en plus sur ``erudit_object``,
il faut ajouter un nouveau niveau de cache: la cache ``erudit_object``. Les ``erudit_object``
post-load sont cachés avec une invalidation d'une heure. 

Ça permet de faire en sorte que l'apport plus important qu'apporte notre instance Fedora à la
génération des vues n'impacte pas trop nos performances.

Ça veut aussi dire que la cache est devenue indispensable au bon fonctionnement du site.
D'invalider entièrement la cache fait en sorte que certaines vues (comme le listing des revues)
vont être très très longues à générer.

liberuditarticle
----------------

Certain champs de l'objet Fedora sont en format XML.
Nous utilisons la librairie `liberuditarticle`_ pour extraire l'information pertinente des objets Fedora.

.. _liberuditarticle: https://www.github.com/erudit/liberuditarticle

Solr
----

Cette section décrit les champs d'un document indexé dans Solr.

Correspondance entre le document indexé dans Solr et les modèles Django
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On utilise les identifiants de l'article pour faire la correspondance entre le document Solr, Django et Fedora.

* ``ID``: identifie l'article dans Fedora. Correspond au :py:attr:`~erudit.models.core.EruditDocument.localidentifier`  d'un :py:class:`~erudit.models.core.Article` 
* ``NumeroID``: identifie le numéro dans Fedora. Correspond au :py:attr:`localidentifier <erudit.models.core.Issue.localidentifier>` d'un :py:class:`Issue <erudit.models.core.Issue>`
* ``RevueID`` identifie la publication dans Fedora. Correspond à :py:attr:`localidentifier <erudit.models.core.Journal.localidentifier>` de :py:class:`Journal <erudit.models.core.Journal>`


Recherche générale
^^^^^^^^^^^^^^^^^^
* ``Titre_fr``, ``Titre_en``: titres de l'article en français et en anglais;
* ``Resume_fr``, ``Resume_en``: résumé de l'article en français et en anglais;
* ``Auteur_tri``: (*à vérifier*) auteur principal de l'article;
* ``Auteur_fac``: liste des auteurs de l'article;
* ``AuteurNP_fac``: (*à vérifier*) liste des auteurs de l'article dans un format plus pratique pour la citation;
* ``Affiliation_fac``: affiliation de l'auteur;
* ``RefBiblio_aff``: références bibliographiques de l'article;
* ``ISSNNum``: ISSN de l'article;
* ``ISBNNum``: ISBN du livre;

À identifier: mots clé, ouvrage recensé.

Recherche par **Types**
^^^^^^^^^^^^^^^^^^^^^^^

* ``Corpus_fac``: identifie le corpus duquel fait partie le document. Utilisé pour faire la recherche par **type**. Prend une des valeurs suivantes:
    * ``Article``: article de revue scientifique;
    * ``Culturel``: article de revue culturelle;
    * ``Actes``: actes de colloque;
    * ``Thèses``: thèses;
    * ``Livres``: livres;
    * ``Depot``: document déposé dans le dépôt de données (littérature grise)


Recherche par **Date**
^^^^^^^^^^^^^^^^^^^^^^

* ``AnneePublication``: année de publication de l'article;
* ``DateAjoutErudit``: date d'ajout de l'article dans érudit

Recherche par **Fonds**
^^^^^^^^^^^^^^^^^^^^^^^

* ``Fonds_fac``: identifie le fond duquel l'article fait partie. Utilisé pour la recherche par **fonds**. Prend une des valeurs suivantes:
    * ``Érudit``: stocké sur Érudit;
    * ``UNB``: *University of New-Brunswick*;
    * ``Persée``: Persée;
