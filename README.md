[![build status](https://gitlab.erudit.org/erudit/portail/eruditorg/badges/master/build.svg)](https://gitlab.erudit.org/erudit/portail/eruditorg/commits/master)
[![Coverage](https://codecov.io/github/erudit/eruditorg/coverage.svg?branch=master)](https://codecov.io/github/erudit/eruditorg?branch=master)
[![Documentation Status](https://readthedocs.org/projects/eruditorg/badge/?version=latest)](http://eruditorg.readthedocs.org/fr/latest/?badge=latest)

This readme only contains installation instructions for more information please refer to the [full documentation](https://eruditorg.readthedocs.org)

# Installing on Ubuntu 14.04

## Make sure git is installed:

  ```
  $ sudo apt-get install git
  ```

## Clone the repository:

  ```
  $ git clone https://github.com/erudit/eruditorg.git
  ```

## Install the system dependencies:

```
$ sudo apt-get install -y python3.4-venv python3-dev mariadb-server libxml2-dev libxslt1-dev zlib1g-dev python3-pip
```

## Setup the virtualenv

Create the virtualenv:

```
$ python3 -m venv env
```

Activate the virtualenv:

```
$ . env/bin/activate
```

Install the project dependencies:

```
$ pip install -r requirements.txt
```

## Database

First, create the database:

```
$ mysql
$ create database eruditorg character set utf8;
```

### Using the default configuration

The default configuration connects to database `eruditorg` with user `root` and no password.
If you do not want this, and would rather use a password, please follow the [mariadb documentation](https://mariadb.com/kb/en/mariadb/set-password/) on how to create a user and update the `settings.py` file accordingly.

## Django

Run the migrations:

```
$ python eruditorg/manage.py migrate
```

Create a superuser:

```
$ python eruditorg/manage.py createsuperuser
```

You can now run the development server

```
$ python eruditorg/manage.py runserver
```

## Retrieving documents and setting up the search engine

Erudit stores its documents in [Fedora Commons](http://www.fedorarepository.org/) and uses the [Solr](http://lucene.apache.org/solr/) search platform. If you need to work on a part of the project that is related to any of these parts, we provide a virtual machine with the required tools.

### Installing the developer virtual machine (VM)

Clone the developer VM.

```
$ git clone git@github.com:erudit/vm-dev.git
```

Follow the instructions in the `vm-dev` project's [README.md](https://github.com/erudit/vm-dev/blob/master/README.md)

Log in the VM.

```
$ vagrant ssh
```

In the VM, clone the `vm-config` project:

```
$ GIT_SSL_NO_VERIFY=true git clone https://gitlab.erudit.team/erudit/vm-config.git
```

*Note: this repository is private. If you need credentials, ask us on IRC.*

Follow the instructions in `vm-config`' [README.md](https://gitlab.erudit.team/erudit/vm-config/blob/master/README.md).

### Using the developer VM

The developer VM provides two services: Fedora Commons and Solr.

* Solr is located at `http://192.168.10.150:8080/solr/`
* Fedora is located at `http://192.168.10.150:8080/fedora/`

### Connecting to Fedora and Solr from Django

*TBD*

# Managing dependencies

## External dependencies

Outside of `pip`-installed dependencies these programs are also needed:

* `qpdf` for PDF generation.

## Updating pip requirements

The `requirements.txt` file is generated with [pip-tools][pip-tools] from `requirements.in`. The
reason for this is that we want to describe main dependencies manually (in `requirements.in`) but
we want to manage transitive dependencies and pinning automatically.

To update `requirements.txt`, ensure you have `pip-tools` installed and run:

```
$ ./tools/update-requirements.sh
```

You should then have a `requirements.txt` with up-to-date dependency pinnings. You can run `pip
install -r requirements.txt` to update your venv.

# Documentation

The project's documentation is built with [Sphinx](http://www.sphinx-doc.org/)

Building the documentation is optional. For this reason, `sphinx` is not listed in requirements.txt
If you wish to build the documentation, you must first install sphinx in your virtualenv.

  ```
  $ pip install sphinx
  ```

You will then be able to build the docoumentation using the `Makefile` in the `docs` directory:

  ```
  $ make html
  ```

# Running the tests

You can run the tests with:

```
$ tox
```

# Documentation

Please visit http://eruditorg.readthedocs.org/fr/latest/

# Contributing patches

Please refer to CONTRIBUTING.md for contribution guidelines.

# Additional information

If you have further questions or if you wish to discuss the project, please join us on **#erudit** on [Freenode](http://www.freenode.org/).

[pip-tools]: https://github.com/jazzband/pip-tools
