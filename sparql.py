import requests, sys, json, codecs


dbpediaEndpoint = "http://live.dbpedia.org/sparql"
inputURIs = "sample.json"
outputFileName = "output.json"

def requete(listURI):
# Requête SPARQL
	payload = {
		"query": """SELECT DISTINCT ?s ?p ?o
					WHERE {
						
						?s a <http://dbpedia.org/ontology/Film>.
						?s ?p ?o.
						?s ?nimp ?uri.
						FILTER (?uri IN """ + listURI + """).
						
					} LIMIT 250
					OFFSET 5000""",
		"format": "json",
		"timeout": "30000"
	}

	response = requests.get(dbpediaEndpoint, params = payload)

	responseJson = response.json()

	with open(outputFileName, "w") as myfile:
		myfile.write(json.dumps(responseJson))

def main():

	# Lecture des URIs

	with open(inputURIs, "r") as myfile:
		jsonContent = myfile.read()
	jsonObject = json.loads(jsonContent)

	

	for page in jsonObject["pages"]:
		listURI = "("
		print(page["url"] + " --- " + str(page["uri"]))
		for uri in page["uri"]:
			listURI += "\"" + uri + "\","
		listURI=listURI[0:-1] + ")"
		print(listURI)
		requete(listURI)


	print(listURI)
	# Requête SPARQL





main()
