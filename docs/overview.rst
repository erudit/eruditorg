Aperçu du modèle de données
===========================

Cette section décrit les liens entre Fedora Commons, Solr, Django, eulfedora,
et liberuditarticle.

En bref
-------

* Le projet Django a des modèles qui décrivent les objets stockés dans Fedora Commons;
* Tous les articles et revues sont stockées dans Fedora Commons;
* Le projet Django utilise eulfedora pour récupérer les objets Fedora Commons;
* La librairie liberuditarticle est utilisée pour parser le contenu des articles;
* Les documents Solr sont des descriptions des articles;


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

TODO
