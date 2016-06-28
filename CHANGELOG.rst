Changelog
#########

0.1.7 - Under development
-------------------------

* Simplify the journal providers settings and replace them by a single ``JOURNAL_PROVIDERS`` setting
* Add the ``Thesis`` model
* Add the ``import_theses_from_oai`` command
* Add a ``logo`` field to the ``Collection`` model
* Fix the ``has_coverpage`` property on the ``Issue`` model

0.1.6
-----

* Adds a ``publication_allowed_by_authors`` field on the ``Article`` model
* Fixed an error occuring when searching for Journal instances through the Django admin

0.1.5
-----

* Improve the ``has_coverpage`` property when the Fedora repository is not available

0.1.4
-----

* Adds a ``thematic_issue`` field to the ``Issue`` model and update the ``import_journals_from_fedora`` command
* Adds a ``has_coverpage`` property on the ``Issue`` model

0.1.3
-----

* Adds a ``type`` field to the ``Article`` model and update the ``import_journals_from_fedora`` command
* Remove old ``get_absolute_url`` methods

0.1.2
-----

* Adds a DisciplineFatory to test disciplines

0.1.1
-----

* Adds a SizeConstrainedImageField model field to define ImageField fields with size and dimensions constraints
* Forces Organisation.badge images to be redimensioned to 140x140 pixels
* Add a missing migration related to the deletion of the Event model
