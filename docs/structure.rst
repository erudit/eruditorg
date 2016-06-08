Structure générale
==================

Aperçu::

  .
  ├── apps
  │   ├── public
  │   │   ├── journal
  │   │   │   ├── templates
  │   │   │   └── tests
  │   └── userspace
  │       └── journal
  │           └── tests
  ├── base
  │   ├── migrations
  │   ├── settings
  │   └── tests
  ├── core
  │   └── journal
  │       └── tests
  └── templates
      ├── base.html
      ├── base_email.html
      ├── 404.html
      ├── 500.html
      ├── partials
      ├── emails
      │   └── journal
      │       └── ...
      │   └── subscription
      │       └── ...
      ├── public
      │   ├── base.html
      │   └── journal
      └── userspace
          ├── base.html
          └── journal

Composantes
-----------

**apps**

Applications du projet. Se séparer en ``userspace``, l'espace utilisateur privé,
et ``public``, le site public.

**base**

La base du projet. Contient les settings, les context_processor, etc.

**core**

Contient les modèles qui sont utilisés par les apps.

**templates**

Les templates du projet. Réplique la hiérarchie qui est sous apps. Il convient de noter que les emails envoyés depuis l'application Érudit doivent hériter du template ``base_email.html`` et doivent être rangés par application logique sous le répertoire "emails".
