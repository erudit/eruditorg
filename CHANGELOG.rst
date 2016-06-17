Changelog
#########

0.1.4 - Under development
-------------------------

* Adds a ``thematic_issue`` field to the ``Issue`` model and update the ``import_journals_from_fedora`` command

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
