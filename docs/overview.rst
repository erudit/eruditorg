Aperçu du modèle de données
===========================

Cette section décrit les liens entre Fedora Commons, Solr, Django, eulfedora et liberuditarticle.

Résumé
------

* Les modèles Django décrivent les objets stockés dans Fedora Commons;
* Les articles et revues sont stockées dans Fedora Commons;
* Django utilise eulfedora pour récupérer les objets Fedora Commons;
* liberuditarticle est utilisé pour parser le contenu des articles;
* Les documents Solr sont des descriptions des objets Fedora Commons.

Modèles Django
--------------

Les trois modèles suivants sont utilisés pour récupérer les données:

* :py:class:`Journal <erudit.models.core.Journal>` (une revue, scientifique ou savante)
* :py:class:`Issue <erudit.models.core.Issue>` (une publication de cette revue)
* Article (*n'est pas encore implémenté*)

Récupération des données dans Fedora
------------------------------------

Les modèles Django implémentent le :py:class:`FedoraMixin <erudit.fedora.modelmixins.FedoraMixin>`.
Le mixin implémente une méthode ``get_full_identifier()`` qui retourne l'identifiant qui permet de récupérer l'objet dans Fedora.
``FedoraMixin`` utilise la librairie `eulfedora`_. pour se connecter à ``Fedora``
et retourne un objet d'un type défini dans le module :py:mod:`erudit.fedora.objects`
Chaque type d'objet contenu dans Fedora présente des particularités.
Le module :py:mod:`objects <erudit.fedora.objects>` permet de faire abstraction de ces particularités.

Par exemple, on peut accéder à la page couverture d'un numéro avec le code suivant::

    issue.get_fedora_object().coverpage


.. _eulfedora: https://www.github.com/emory-libraries/eulfedora

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

* ``ID``: identifie l'article dans Fedora. Correspond au ``localidentifier``  d'un ``Article`` (*pas encore implémenté*)
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
    * ``article``: article de revue scientifique;
    * ``culturel``: article de revue culturelle;
    * ...


Recherche par **Date**
^^^^^^^^^^^^^^^^^^^^^^

* ``AnneePublication``: année de publication de l'article;
* ``DateAjoutErudit``: date d'ajout de l'article dans érudit

Recherche par **Fonds**
^^^^^^^^^^^^^^^^^^^^^^^

* ``Fonds_fac``: identifie le fond duquel l'article fait partie. Utilisé pour la recherche par **fonds**. Prend une des valeurs suivantes:
    * ``Érudit``: stocké sur Érudit;
    * ...
