import requests, sys, json, codecs


dbpediaEndpoint = "http://live.dbpedia.org/sparql"
inputURIs = "sample.json"
outputFileName = "output.json"

def requete(listURI):
# Requête SPARQL

	struct = {}
	struct['link'] = 'http:zbbooob'
	struct['results'] = {}
	struct['results']['graphePage'] = []
	struct['results']['films'] = []

	

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

	responseJson = response.json()
	
	jacky = {}
	jacky['link']='toto'
	jacky['graphe'] = responseJson['results']['bindings']
	
	return jacky

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
		listURI=listURI[0:-1] + ")"
		#print(listURI)
		struct['results']['films'].append(requete(listURI))
		sortie.append(struct)


	#print(listURI)
	with open(outputFileName, "w") as myfile:
		myfile.write(json.dumps(sortie))
	# Requête SPARQL





main()
