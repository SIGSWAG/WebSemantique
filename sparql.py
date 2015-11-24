import requests, sys, json, codecs


dbpediaEndpoint = "http://live.dbpedia.org/sparql"
inputURIs = "sample.json"
outputFileName = "output.json"

def requetePage(uri):
# Requête SPARQL	

	
	payload = {
		"query": """SELECT DISTINCT (""" + uri + """ as ?s) ?p ?o
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

def requeteFilms(listURI):
# Requête SPARQL	

	payload = {
		"query": """SELECT DISTINCT ?s ?p ?o
					WHERE {
						
						?s a <http://dbpedia.org/ontology/Film>.
						?s ?p ?o.
						
					} LIMIT 250
					OFFSET 5000""",
		"format": "json",
		"timeout": "30000"
	}

	response = requests.get(dbpediaEndpoint, params = payload)
	
	if(response.status_code==200):
		responseJson = response.json()
		
		jacky = {}
		jacky['link']= responseJson['results']['bindings'][0]['s']['value']
		jacky['graphe'] = responseJson['results']['bindings']
		
		return jacky
	else:
		return {}

def main():

	# Lecture des URIs
	sortie = []

	with open(inputURIs, "r") as myfile:
		jsonContent = myfile.read()
	jsonObject = json.loads(jsonContent)

	

	

	for page in jsonObject["pages"]:
		listURI = "("
		#print(page["url"] + " --- " + str(page["uri"]))
		
		struct = {}
		struct['link'] = page["url"]
		struct['results'] = {}
		struct['results']['graphePage'] = []
		struct['results']['films'] = []
		
		for uri in page["uri"]:
			listURI += "\"" + uri + "\","
			struri = "<" + uri + ">"
			struct['results']['graphePage']+=requetePage(struri)
		listURI=listURI[0:-1] + ")"
		#print(listURI)
		struct['results']['films'].append(requeteFilms(listURI))
		sortie.append(struct)


	#print(listURI)
	with open(outputFileName, "w") as myfile:
		myfile.write(json.dumps(sortie))
	# Requête SPARQL





main()
