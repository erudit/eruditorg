[![build status](https://gitlab.erudit.org/erudit/portail/eruditorg/badges/master/build.svg)](https://gitlab.erudit.org/erudit/portail/eruditorg/commits/master)
[![Coverage](https://codecov.io/github/erudit/eruditorg/coverage.svg?branch=master)](https://codecov.io/github/erudit/eruditorg?branch=master)
[![Documentation Status](https://readthedocs.org/projects/eruditorg/badge/?version=latest)](http://eruditorg.readthedocs.org/fr/latest/?badge=latest)

This readme only contains installation instructions for more information please refer to the [full documentation](https://eruditorg.readthedocs.org)

# Installation

## Requirements

* Python 3.5+
* Maria DB
* libxml
* libxslt
* zlib
* git
* libffi-dev
* qpdf for PDF generation
* An access to our Solr database
* An access to our Fedora repository

Those last two requirements mean that unless you spend time building yourself a Solr and Fedora
instances, you can't really run this app locally if you're not part of Érudit.

On Ubuntu 18.04, requirements can be installed with:

    $ sudo apt-get install -y python3-venv python3-dev mariadb-server libxml2-dev libxslt1-dev zlib1g-dev git libffi-dev

## Clone the repository:

  ```
  $ git clone https://github.com/erudit/eruditorg.git
  ```

## Setup the virtualenv

This step is taken care of by the Makefile, so:

    $ make

will create the virtualenv and install python dependencies in it.

## Database

then, you need a database:

    $ mysql
    $ create database eruditorg character set utf8;

## Initial data

The easiest way to seed your development environment is to import a dump from the production server
into your local database. Generating local data from scratch is possible, but its seldom done so
this road is bumpy. To import a dump in mysql:

    $ gzip -dc dump.sql.gz | mysql -u root -D eruditorg

## Creating settings_env.py

Copy `eruditorg/base/settings/setting_env.py.sample` into `eruditorg/base/settings/settings_env.py`
and edit this file with credentials to Érudit's Solr and Fedora instances. You can also override
base settings in it.

The default configuration connects to database `eruditorg` with user `root` and no password.
If you do not want this, and would rather use a password, follow the
[mariadb documentation](https://mariadb.com/kb/en/mariadb/set-password/) on how to create a user
and update the `settings_env.py` file accordingly.

## Django

Activate the virtualenv:

    $ . env/bin/activate

Run the migrations:

    $ python eruditorg/manage.py migrate

You can now run the development server

    $ python eruditorg/manage.py runserver

# Updating pip requirements

The `requirements.txt` file is generated with [pip-tools][pip-tools] from `requirements.in`. The
reason for this is that we want to describe main dependencies manually (in `requirements.in`) but
we want to manage transitive dependencies and pinning automatically.

To update `requirements.txt`, ensure you have `pip-tools` installed and run:

    $ ./tools/update-requirements.sh

You should then have a `requirements.txt` with up-to-date dependency pinnings. You can run `pip
install -r requirements.txt` to update your venv.

# Documentation

The project's documentation is built with [Sphinx](http://www.sphinx-doc.org/)

Building the documentation is optional. For this reason, `sphinx` is not listed in requirements.txt
If you wish to build the documentation, you must first install sphinx in your virtualenv.

  $ pip install sphinx

You will then be able to build the docoumentation using the `Makefile` in the `docs` directory:

  $ make html

# Running the tests

You can run the tests with:

    $ tox

Tests are ran with pytest. You can pass arguments to pytest through tox with `--`. For example, if
you want to run tests using 4 cores in parallel and stopping at the first failure, you would run:

    $ tox -- -x -n4

# Documentation

Please visit http://eruditorg.readthedocs.org/fr/latest/

# Contributing patches

Please refer to CONTRIBUTING.md for contribution guidelines.

# Additional information

If you have further questions or if you wish to discuss the project, please join us on **#erudit** on [Freenode](http://www.freenode.org/).

[pip-tools]: https://github.com/jazzband/pip-tools
