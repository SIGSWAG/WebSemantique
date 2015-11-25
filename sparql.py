import requests, sys, json, codecs, rdflib


dbpediaEndpoint = "http://live.dbpedia.org/sparql"
inputURIs = "sample.json"
outputFileName = "output.json"
grapheAlternatif = rdflib.Graph()
grapheAlternatif.parse("baseAlternative.rdf", format="nt")


		
def requetePage(uri):
# Requête SPARQL	

	
	payload = {
		"query": """SELECT DISTINCT ("""+uri+""" as ?s) ?p ?o
					WHERE {
						
						"""+uri+""" ?p ?o.
						
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
		
		

def chercheFilms(uri):
# Requête SPARQL	

	payload = {
		"query": """SELECT DISTINCT ?s
					WHERE {
						
						?s a <http://dbpedia.org/ontology/Film>.
						?s ?p <"""+ uri +""">.
						
					} LIMIT 5
					""",
		"format": "json",
		"timeout": "30000"
	}

	response = requests.get(dbpediaEndpoint, params = payload)
	
	if(response.status_code==200):
		print("yo")
		responseJson = response.json()
		
		filmsURI = []
		

		try:
			for film in responseJson['results']['bindings'][0]['s']['value']:
				jacky = {}
				jacky['link']= film
				jacky['graphe'] = {}
				jacky["graphe"].append(requeteFilm(film))
				filmsURI.append(jacky)
		except:
			return []
			
			
		return filmsURI
	else:
		return {}
		
		
def chercheFilmsAlternatif(uri):
	qres = g.query(
		"""SELECT DISTINCT ?s
		   WHERE {
		   ?s ?p <"""+ uri +""">.
		   }LIMIT 5""")

	graphe = []
		
	for s, p, o in qres:
		
		lien = {}
		lien["s"]={}
		lien["s"]["value"]=s
		lien["s"]["type"]="uri"
		lien["p"]={}
		lien["p"]["value"]=p
		lien["p"]["type"]="uri"
		lien["o"]={}
		lien["o"]["value"]=o
		lien["o"]["type"]="uri"
		graphe.append(lien)
		
	return graphe
		
		

def requeteFilm(uriFilm):
# Requête SPARQL	

	payload = {
		"query": """SELECT DISTINCT (("""+uriFilm+""") as ?s) ?p ?o
					WHERE {
						
						
						"""+uriFilm+""" ?p ?o.
						
					} LIMIT 250
					""",
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
		
		films={}
		
		for uri in page["uri"]:
			struri = "<" + uri + ">"
			struct['results']['graphePage']+=requetePage(struri)
			struct["results"]["films"]+=chercheFilms(uri)
			

		sortie.append(struct)


	#print(listURI)
	with open(outputFileName, "w") as myfile:
		myfile.write(json.dumps(sortie))
	# Requête SPARQL





main()
