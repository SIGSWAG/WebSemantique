# WebSemantique

## Intallations requises

	Python3

### Librairies Python3 requises

Le projet nécessite rdflib et rdflib-jsonld pour fonctionner. Pour installer ces libs via pip3 (pip pour Python3) :

```bash
pip3 install rdflib==4.2.1
pip3 install rdflib-jsonld==0.3
```

## Lancement du serveur
```bash
cd web
python3 -m http.server --cgi
```

Ouvrir un navigateur à l'adresse : [localhost:8000](http://localhost:8000)

Attention le fichier web/cgi-bin/server.py doit avoir les droits d'execution.

## Execution de l'application en ligne de commande

Lancer l'application avec le mot clef "robot" en utilisant Bing (search_type=2) avec 5 résultats au maximum.
Tous les autres paramètres sont obligatoires.

```bash
cd appli
python3 main.py --mots_clefs="robot" --max_number_of_results=5 --search_type=2 --spotlight_confidence=0.1 --from_web=true --spotlight_support=20 --append_keyword=false
```