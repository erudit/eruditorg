# Contributing to Erudit.org

## Documentation

* Does the documentation build? Does `make html` return errors?

## Fixing bugs

* Is there a proper regression test?

## Adding new features

* Is the feature documented?

## Internationalization

* Are the strings internationalized?
* Is the base language of strings French?

## Code changes

* Does the coding style conform to the guidelines? Are there any flake8 errors?
* Is the test suite passing?
* Is the code exempt of spurious print / console.log statements?
* Do HTTP requests to internal services have explicite timeout set ?

## Git

* Does the commit message follow the project [standards](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)?

## Developing the UI

* Does the front-end generally follow these [guidelines](https://github.com/bendc/frontend-guidelines)?
* Does the Sass respect the [7-1 architecture pattern](http://sass-guidelin.es/#architecture)?
* Do the classes adhere to a consistent naming convention using hyphens for Sass and camelCase for JavaScript?
** Do the code follow the project's [javascript development guidelines](eruditorg.readthedocs.org/fr/latest/javascript.html) ?

## Translations

* Do the PO files include translations for the XSL documents?

## URLs

* Do the URL names consist only of letters and underscores?

## Templates

* Do the template names consist only of letters and underscores?
* Are the template "partials" located inside "partials" directories?
