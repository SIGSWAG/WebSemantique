import requests, sys, json, codecs, rdflib


dbpediaEndpoint = "http://live.dbpedia.org/sparql"
inputURIs = "sample.json"
outputFileName = "output.json"
grapheAlternatif = rdflib.Graph()
grapheAlternatif.parse("baseAlternative.rdf", format="nt")

def construitGrapheFilm(uri):
	jacky = {}
	jacky['link']= uri
	jacky['graphe'] = []
	jacky["graphe"]+=requeteFilm(uri)
	jacky["graphe"]+=requeteFilmAlternative(uri)
	jacky["infos"]=requeteInfoMovie(uri)
	return jacky

	
def requeteInfoMovie(uri):
# Requête SPARQL	

	
	payload = {
		"query": """select distinct * where {

				<"""+uri+"""> <http://xmlns.com/foaf/0.1/name> ?name


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
	
		
def requetePage(uri):
# Requête SPARQL	
	
	payload = {
		"query": """SELECT DISTINCT (<"""+uri+"""> as ?s) ?p ?o
					WHERE {
						
						<"""+uri+"""> ?p ?o.
						
					} LIMIT 10
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
		responseJson = response.json()
		
		filmsURI = []
		

		try:
			for film in responseJson['results']['bindings'][0]['s']['value']:
				filmsURI.append(construitGrapheFilm(film))
		except:
			return []
			
			
		return filmsURI
	else:
		return {}
		
		
def chercheFilmsAlternatif(uri):

	qres = grapheAlternatif.query(
		"""SELECT DISTINCT ?s
		   WHERE {
		   ?s ?p <"""+ uri +""">.
		   }LIMIT 5""")

	filmsURI = []

	try:	
		for s in qres:
			filmsURI.append(construitGrapheFilm(s[0]))
		
	except:
		return []
		
	return filmsURI	
		
		

def requeteFilm(uriFilm):
# Requête SPARQL	


	payload = {
		"query": """SELECT DISTINCT (<"""+uriFilm+"""> as ?s) ?p ?o
					WHERE {
						
						
						<"""+uriFilm+"""> ?p ?o.
						
					} LIMIT 10
					""",
		"format": "json",
		"timeout": "30000"
	}
	

	response = requests.get(dbpediaEndpoint, params = payload)
	
	if(response.status_code==200):
		responseJson = response.json()
		
		return responseJson['results']['bindings']
	else:
		return {}
		
		
def requeteFilmAlternative(uriFilm):
# Requête SPARQL	

	qres = grapheAlternatif.query(
		"""SELECT DISTINCT (<"""+uriFilm+"""> as ?s) ?p ?o
		   WHERE {
		   <"""+uriFilm+"""> ?p ?o.
		   }LIMIT 10""")

	graphe = []

	try:	
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

	except:
		return []
		
	return graphe
		

def main():

	# Lecture des URIs
	sortie = []

	with open(inputURIs, "r") as myfile:
		jsonContent = myfile.read()
	jsonObject = json.loads(jsonContent)

	

	

	for page in jsonObject["pages"]:
		listURI = "("

		
		struct = {}
		struct['link'] = page["url"]
		struct['results'] = {}
		struct['results']['graphePage'] = []
		struct['results']['films'] = []
		
		
		#Pour chaque URI, on enrichit le graphe de la page, et on cherche 5 films max dans dbpedia,
		#et dans le graphe alternatif, qui sont liés à l'uri
		for uri in page["uri"]:
			struct['results']['graphePage']+=requetePage(uri)
			struct["results"]["films"]+=chercheFilms(uri)
			struct["results"]["films"]+=chercheFilmsAlternatif(uri)
			

		sortie.append(struct)


	with open(outputFileName, "w") as myfile:
		myfile.write(json.dumps(sortie))
	# Requête SPARQL





main()
