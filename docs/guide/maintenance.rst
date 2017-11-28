Mode maintenance
================

La plateforme Érudit dispose d'un mode maintenance. Lorsque le mode maintenance est activé, toutes les opérations d'écriture sont désactivées, et un bandeau s'affiche pour avertir les utilisateurs que le contenu du site n'est peut-être pas à jour.

Pour activer le mode maintenance:

1. Dans l'interface d'administration de Django, créer un ``Switch``
2. Créer un switch ``maintenance`` et l'activer.
3. Le site est en mode maintenance.

Pour désactiver le mode maintenance:

1. Dans l'interface d'aministration, désactiver le ``Switch`` ``maintenance``.
