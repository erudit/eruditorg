Envoi de courriels
==================

Les courriels envoyés via l'application Érudit doivent être déclarés au moyent du helper ``core.email.Email``. Voici un exemple d'utilisation :

::

  from core.email import Email

  email = Email(
    ['foo@bar.xyz', ],
    html_template='path/to/content_template.html',
    subject_template='path/to/subject_template.html',
    extra_context={'foo': 'bar'})
  email.send()  # Triggers the sending

Référence
---------

 .. automodule :: core.email.email
    :members:
