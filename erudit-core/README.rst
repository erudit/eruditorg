===========
erudit-core
===========

.. image:: http://img.shields.io/travis/erudit/erudit-core.svg?style=flat-square
    :target: http://travis-ci.org/erudit/erudit-core
    :alt: Build status

.. image:: https://img.shields.io/codecov/c/github/erudit/erudit-core.svg?style=flat-square
    :target: https://codecov.io/github/erudit/erudit-core
    :alt: Codecov status

*A Django application that defines the core entities of the Érudit platform.*

.. contents::

Requirements
------------

* Python 3.4+
* Django 1.8+

Installation
------------

Just run:

::

  pip install git+git://github.com/erudit/erudit-core.git

Once installed you just need to add ``modeltranslation`` and ``erudit`` to ``INSTALLED_APPS`` in your project's settings module:

::

  INSTALLED_APPS = (
      # other apps
      'modeltranslation',
      'erudit',
  )

Then install the models:

::

    python manage.py migrate erudit

*Congrats! You’re in!*


Authors
-------

Érudit Consortium <tech@erudit.org> and contributors_

.. _contributors: https://github.com/erudit/erudit-core/graphs/contributors

License
-------

GNU General Public License v3 (GPLv3). See ``LICENSE`` for more details.
