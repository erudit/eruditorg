Structure générale
==================

Aperçu::

  .
  ├── apps
  │   ├── public
  │   │   ├── journal
  │   │   │   ├── templates
  │   ├── userspace
  │   │   └─ journal
  │   └─ webservices
  │       └-─ sushi
  ├── base
  │   ├── migrations
  │   ├── settings
  │   └── test
  ├── core
  │   └── journal
  ├── erudit
  │   └── test
  ├── templates
  │   ├── base.html
  │   ├── base_email.html
  │   ├── 404.html
  │   ├── 500.html
  │   ├── partials
  │   ├── emails
  │   │   └── journal
  │   │       └── ...
  │   │   └── subscription
  │   │       └── ...
  │   ├── public
  │   │   ├── base.html
  │   │   └── journal
  │   └── userspace
  │       ├── base.html
  │       └── journal
  └── tests

Composantes
-----------

**apps**

Applications du projet. Se séparer en ``userspace``, l'espace utilisateur privé,
et ``public``, le site public.

**base**

La base du projet. Contient les settings, les context_processor, etc.

**core**

Contient les modèles qui sont utilisés par les apps.

**erudit**

Contient les modèles de base ``Journal``` ``Issue`` ``Article`` etc. Logiquement, pourrait être
fusionné à ``core`` mais est séparé parce qu'historiquement il était dans un dépôt de source
externe.

**templates**

Les templates du projet. Réplique la hiérarchie qui est sous apps. Il convient de noter que les emails envoyés depuis l'application Érudit doivent hériter du template ``base_email.html`` et doivent être rangés par application logique sous le répertoire "emails".

**test**

``erudit`` et ``base`` contiennent un sous-package ``test`` qui contient des utilitaires de tests
comme par exemple des factories et des mocks.

**tests**

Les tests du projet. Se divise en tests fonctionnels et en tests unitaires. La structure des tests de chacune de ces catégories réplique la hiérarchie qui est sous apps.
