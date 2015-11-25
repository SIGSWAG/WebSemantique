import requests, sys, json, codecs, rdflib, os


dbpediaEndpoint = "http://live.dbpedia.org/sparql"
inputURIs = os.path.join("sparql", os.path.join("sample_output", "sample.json"))
outputFileName = os.path.join("sparql", os.path.join("sample_output", "sparql.txt"))
grapheAlternatif = rdflib.Graph()
grapheAlternatif.parse(os.path.join("sparql", "baseAlternative.rdf"), format="nt")
nombreLiensParURI = '50'
nombreFilmsDBPedia = '5'
nombreFilmsAlternatif = '5'
nombreLiensFilmsDBPedia = '100'
nombreLiensFilmsAlternatif = '100'


def construitGrapheFilm(uri):
	jacky = {}
	jacky['link']= uri
	jacky['graphe'] = []
	jacky["graphe"]+=requeteFilm(uri)
	jacky["graphe"]+=requeteFilmAlternative(uri)
	jacky["infos"]=requeteInfoMovie(uri)
	print(jacky["infos"])
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
		nombreFilmsAlternatif = '5'
		
	if(4 < len(sys.argv)):
		nombreLiensFilmsDBPedia = sys.argv[3]
	else:
		nombreLiensFilmsDBPedia = '100'
		
	if(5 < len(sys.argv)):
		nombreLiensFilmsAlternatif = sys.argv[3]
	else:
		nombreLiensFilmsAlternatif = '100'

	with open(outputFileName, "r") as myfile:
		json = myfile.read()
		main(json)
