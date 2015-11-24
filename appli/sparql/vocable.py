
//trouver des films

select distinct ?s  where {

?s a <http://dbpedia.org/ontology/Film>
} LIMIT 100

//trouver des choses
select distinct ?s  where {

?s a ?p
} LIMIT 100

//calculer le vocabulaire ?
Mettre toutes les URIS De 1 dans un set
Mettre toutes les URIS de 2 dans un set
Faire la différence entre ces deux set


dbpediaEndpoint = "http://live.dbpedia.org/sparql"
mainPredicate = "<http://dbpedia.org/ontology/Film>"
def requetePage(uri):
# Requête SPARQL	

	
	payload = {
		"query": """SELECT DISTINCT *
					WHERE {
						
						
						""" + uri + """ ?p ?o.
						
					} LIMIT 250
					""",
		"format": "json",
		"timeout": "30000"
	}


	response = requests.get(dbpediaEndpoint, params = payload)

	
	if(response.status_code==200):
		responseJson = response.json()
		
		graphe = responseJson['results']['bindings']
		
		return graphe
	else:
		return []




