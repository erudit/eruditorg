[![Build Status](https://secure.travis-ci.org/erudit/zenon.svg?branch=master)](https://secure.travis-ci.org/erudit/zenon?branch=master)
[![Coverage](https://codecov.io/github/erudit/zenon/coverage.svg?branch=master)](https://codecov.io/github/erudit/zenon?branch=master)

# Installing on Ubuntu 14.04

## Make sure git is installed:

  ```
  $ sudo apt-get install git
  ```

## Clone the repository:

  ```
  $ git clone https://github.com/erudit/zenon.git
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

# Contributing patches

Please refer to CONTRIBUTING.md for contribution guidelines
