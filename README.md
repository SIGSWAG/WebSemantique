# WebSemantique

## Fonctionnement actuel

### Role de chaque module
Chaque module récupère via l'entrée standard la sortie du précédent module (sous forme de JSON).
Un exemple pour chaque module est fourni.
Vous **devez renvoyer votre réponse sous forme de JSON dans la sortie standard**

#### Dossiers sample_output
Dans le dossier sample_output, vous **devez mettre un exemple de JSON** que vous avez généré (grace à votre programme ou à la main). Ainsi toutes les parties sont indépendantes et il n'y a pas besoin de se retaper toute la chaine à chaque fois qu'on veut lancer notre partie.

### Lancement du serveur
		cd web

		python3 -m http.server --cgi

Attention le fichier web/cgi-bin/server.py doit avoir les droits d'execution.

### JSON
Pour récupérer le JSON en web (et donc appeler le chef d'orchestre):

	http://localhost:8000/cgi-bin/server.py?seuil_jordan=0.1&mots_clefs=test

Pour récupérer le JSON en ligne de commande :

	cd appli

	python3 main.py -m 'test' -s 0.3