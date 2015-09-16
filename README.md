# INSTALLATION

On a freshly cloned repository:

You need to create a `settings_env.py` configuration file in `erudit/erudit`. This file requires at least the following:


A database coniguration:

```
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

A `SECRET_KEY` and either a `DEBUG` or an `ALLOWED_HOSTS`:

```
DEBUG = True
SECRET_KEY = 'INSECURE'
```

# Running the tests

You can run the tests with:

```
$ tox
```