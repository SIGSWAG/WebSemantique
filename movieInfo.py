import requests, sys, json, codecs


dbpediaEndpoint = "http://live.dbpedia.org/sparql"

def requeteInfoMovie(uri):
# Requête SPARQL	

	
	payload = {
		"query": """select distinct * where {

				"""+uri+""" <http://xmlns.com/foaf/0.1/name> ?name


				OPTIONAL{

				<http://dbpedia.org/resource/Inception>  <http://dbpedia.org/ontology/director> ?director.
				?director <http://xmlns.com/foaf/0.1/name> ?dirName.
				<http://dbpedia.org/resource/Inception>  <http://dbpedia.org/property/country> ?country.
				<http://dbpedia.org/resource/Inception> <http://dbpedia.org/property/starring> ?starring.
				}
			}
			LIMIT 1
					""",
		"format": "json",
		"timeout": "30000"
	}


	response = requests.get(dbpediaEndpoint, params = payload)

	
	if(response.status_code==200):
		responseJson = response.json()
		
		graphe = responseJson['results']['bindings'][0]
		
		return graphe
	else:
		return []




if __name__ == "__main__":
	
    		print(json.dumps(requeteInfoMovie("<http://dbpedia.org/resource/Inception>")))
