## Qu'est-ce que le MR fait ?

## Comment tester ?

## Screenshots / vidéo

## À valider

### Documentation

* [ ] Est-ce que la documentation compile ? Est-ce que `make html` retourne des erreurs ?

### Correction de bogues

* [ ] Est-ce qu'il y a un test de régression ?

### Nouvelle fonctionnalité

* [ ] Est-ce que la fonctionnalité est documentée ?

### Internationalisation

* [ ] Est-ce que les chaînes de caractères sont internationalisées ?
* [ ] Est-ce que la langue de base est le français ?

### Changements au code

* [ ] Est-ce que black passe ?
* [ ] Est-ce que les tests passent ?
* [ ] Est-ce que tous les print / console.log ont été enlevés ?
* [ ] Est-ce que les requêtes HTTP ont un timeout explicite ?

### Git

* [ ] Est-ce que le message de commit suit les [standards](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html) du projet ?
* [ ] Est-ce que le message de commit est clair et décrit bien les changements ?
* [ ] Est-ce que le MR est exempt de commits qui modifient des commits qui ont été ajoutés dans le même MR ?

### Front-end

* [ ] De manière générale, est-ce que le front-end suit les [guidelines](https://github.com/bendc/frontend-guidelines)?
* [ ] Est-ce que le Sass suit le [7-1 architecture pattern](http://sass-guidelin.es/#architecture)?
* [ ] Est-ce que les classes adhèrent à la convention de nommage: traits d'union pour le Sass et camelCase pour JavaScript?
* [ ] Est-ce que le code suit notre guide  [javascript](eruditorg.readthedocs.org/fr/latest/javascript.html) ?

## Translations

* [ ] Est-ce que les PO incluent les traductions pour le document XSL ? Est-ce que les PO ont été générés avec le script shell ?

## URLs

* [ ] Est-ce que les URLs contiennent uniquement des lettres et des caractères de soulignement ?

## Templates

* [ ] Est-ce que les noms des templates contiennent uniquement des lettres et des caractères de soulignement ?
* [ ] Est-ce que les "partials" sont dans les répertoires "partials" ?
