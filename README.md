[![Build Status](https://secure.travis-ci.org/erudit/eruditorg.svg?branch=master)](https://secure.travis-ci.org/erudit/eruditorg?branch=master)
[![Coverage](https://codecov.io/github/erudit/eruditorg/coverage.svg?branch=master)](https://codecov.io/github/erudit/eruditorg?branch=master)
[![Documentation Status](https://readthedocs.org/projects/eruditorg/badge/?version=latest)](http://eruditorg.readthedocs.org/fr/latest/?badge=latest)

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
$ sudo apt-get install -y python3.4-venv python3-dev postgresql postgresql-server-dev-all libxml2-dev libxslt1-dev zlib1g-dev python3-pip
```

## Setup the virtualenv

Create the virtualenv:

```
$ pyvenv-3.4 env
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
$ sudo su - postgres
$ createdb zenon
$ logout
```

### Using the default configuration

The default configuration connects to database `zenon` with user `postgres` and no password.
If you do not want this, and would rather use a password, please follow the [postgresql documentation](http://www.postgresql.org/docs/8.0/static/sql-createuser.html) on how to create a user and update the `settings.py` file accordingly.

Allow local connections over TCP/IP.

Edit the `pg_hba.conf` file:

```
$ sudo vim /etc/postgresql/9.3/main/pg_hba.conf
```

And replace the following line:

```
host    all             all             127.0.0.1/32            md5
```

With:

```
host    all             all             127.0.0.1/32            trust
```

Reload the postgresql configuration:

```
$ sudo /etc/init.d postgresql reload
```

## Django

Run the migrations:

```
$ python erudit/manage.py migrate
```

Create a superuser:

```
$ python erudit/manage.py createsuperuser
```

You can now run the development server

```
$ python erudit/manage.py runserver
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
$ git clone https://gitlab.erudit.team/erudit/vm-config.git
```

*Note: this repository is private. If you need credentials, ask us on IRC.*

Follow the instructions in `vm-config`' [README.md](https://gitlab.erudit.team/erudit/vm-config/blob/master/README.md).

### Using the developer VM

The developer VM provides two services: Fedora Commons and Solr.

* Solr is located at `http://192.168.10.150:8080/solr/`
* Fedora is located at `http://192.168.10.150:8080/fedora/`

### Connecting to Fedora and Solr from Django

*TBD*

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
