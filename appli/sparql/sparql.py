import requests, sys, json, codecs, rdflib, os


dbpediaEndpoint = "http://live.dbpedia.org/sparql"
inputURIs = os.path.join("sparql", os.path.join("sample_output", "sample.json"))
outputFileName = os.path.join("sparql", os.path.join("sample_output", "sparql.txt"))
grapheAlternatif = rdflib.Graph()
grapheAlternatif.parse(os.path.join("sparql", "baseAlternativeFat.rdf"), format="nt")
nombreLiensParURI = '50'
nombreFilmsDBPedia = '5'
nombreFilmsAlternatif = '10'
nombreLiensFilmsDBPedia = '100'
nombreLiensFilmsAlternatif = '50'
nombreFilmsMotsClefs = '10'


def construitGrapheFilm(uri):
	jacky = {}
	jacky['link']= uri
	jacky['graphe'] = []
	jacky["graphe"]+=requeteFilm(uri)
	jacky["graphe"]+=requeteFilmAlternative(uri)
	jacky["infos"]=requeteInfoMovie(uri)
	return jacky


def cherche_mots_clefs(mots):
# Requête SPARQL	

	filter = ""
	for mot in mots:
		filter += "contains(lcase(?a), \""+mot+"\")&&"
		
	payload = {
		"query": """SELECT DISTINCT ?s
					WHERE {
						
						?s a <http://dbpedia.org/ontology/Film>.
						?s <http://dbpedia.org/ontology/abstract> ?a.
						FILTER(""" + filter[0:-2] + """).
						
					} ORDER BY DESC(fn:string-length(?a)) LIMIT """+nombreFilmsMotsClefs
					,
		"format": "json",
		"timeout": "30000"
	}
	
	# print(payload["query"])

	response = requests.get(dbpediaEndpoint, params = payload)
	
	if(response.status_code==200):
		responseJson = response.json()
		#print(responseJson)
		
		filmsURI = []
		
		for film in responseJson['results']['bindings']:
			try:
				jacky = {}
				jacky['link']= film["s"]["value"]
				jacky["infos"]=requeteInfoMovie(film["s"]["value"])
				filmsURI.append(jacky)
			except:
				jacky = {}
			
		return json.dumps(filmsURI)
	
	
	else:
		return {}
	
	
def requeteInfoMovie(uri):
# Requête SPARQL
	
	payload = {
		"query": """select distinct * where {

				<"""+uri+"""> <http://xmlns.com/foaf/0.1/name> ?name


				OPTIONAL{

				<"""+uri+""">  <http://dbpedia.org/ontology/director> ?director.
				?director <http://xmlns.com/foaf/0.1/name> ?dirName.
				<"""+uri+"""> <http://dbpedia.org/property/country> ?country.
				<"""+uri+"""> <http://dbpedia.org/property/starring> ?starring.
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
						
					} LIMIT """+nombreLiensParURI
					,
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
						
					} LIMIT """+nombreFilmsDBPedia
					,
		"format": "json",
		"timeout": "30000"
	}

	response = requests.get(dbpediaEndpoint, params=payload)
	
	if(response.status_code == 200):
		responseJson = response.json()
		
		filmsURI = []
		

		try:
			for film in responseJson['results']['bindings']:
				node = construitGrapheFilm(film["s"]["value"])
				if node["infos"] is not []:
					filmsURI.append(node)
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
		   }LIMIT """ + nombreFilmsAlternatif)

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
						
					} LIMIT	"""+nombreLiensFilmsDBPedia
					,
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
		   }LIMIT 10""" + nombreLiensFilmsAlternatif)

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
		

def main(jsonContent):
	# Lecture des URIs
	sortie = []
	jsonObject = json.loads(jsonContent)


	for page in jsonObject["pages"]:
		listURI = "("
		
		struct = {}
		struct['link'] = page["url"]
		struct['title'] = page["title"]
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


	with open(outputFileName, "w+") as myfile:
		myfile.write(json.dumps(sortie))
	# Requête SPARQL
	return json.dumps(sortie)

'''
=========================================================================================
Usage 
python sparql.py 
python sparql.py
=========================================================================================
'''
if	__name__ =='__main__':

	if(1 < len(sys.argv)):
		nombreLiensParURI = sys.argv[1]
	else:
		nombreLiensParURI = '50'
	if(2 < len(sys.argv)):
		nombreFilmsDBPedia = sys.argv[2]
	else:
		nombreFilmsDBPedia = '5'

	if(3 < len(sys.argv)):
		nombreFilmsAlternatif = sys.argv[3]
	else:
		nombreFilmsAlternatif = '10'
		
	if(4 < len(sys.argv)):
		nombreLiensFilmsDBPedia = sys.argv[4]
	else:
		nombreLiensFilmsDBPedia = '100'
		
	if(5 < len(sys.argv)):
		nombreLiensFilmsAlternatif = sys.argv[5]
	else:
		nombreLiensFilmsAlternatif = '100'
	if(6 < len(sys.argv)):
		nombreLiensFilmsAlternatif = sys.argv[6]
	else:
		nombreFilmsMotsClefs = '10'

	with open(outputFileName, "r") as myfile:
		json = myfile.read()
		main(json)