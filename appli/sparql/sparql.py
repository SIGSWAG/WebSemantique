import requests, sys, json, codecs, rdflib, os


dbpedia_endpoint = "http://live.dbpedia.org/sparql"
output_file_name = "sample_entry.txt"
graphe_alternatif = rdflib.Graph()
graphe_alternatif.parse(os.path.join("sparql", "baseAlternativeFat.rdf"), format="nt")
nombre_liens_par_URI = '50'
nombre_films_DBPedia = '5'
nombre_films_alternatif = '10'
nombre_liens_films_DBPedia = '100'
nombre_liens_films_alternatif = '50'
nombre_films_mots_clefs = '10'


def construit_graphe_film(uri):
	jacky = {}
	jacky['link']= uri
	jacky['graphe'] = []
	jacky["graphe"]+=requete_film(uri)
	jacky["graphe"]+=requete_film_alternative(uri)
	jacky["infos"]=requete_info_movie(uri)
	return jacky

#Requête qui recherche les mots clés de l'utilisateur dans les dbo:abstract
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
						
					} ORDER BY DESC(fn:string-length(?a)) LIMIT """+nombre_films_mots_clefs
					,
		"format": "json",
		"timeout": "30000"
	}

	response = requests.get(dbpedia_endpoint, params = payload)
	
	if(response.status_code==200):
		response_json = response.json()
		
		films_URI = []
		
		for film in response_json['results']['bindings']:
			try:
				jacky = {}
				jacky['link']= film["s"]["value"]
				jacky["infos"]=requete_info_movie(film["s"]["value"])
				films_URI.append(jacky)
			except:
				jacky = {}
			
		return json.dumps(films_URI)
	
	
	else:
		return {}
	
	
#Requête qui cherche les informations de la détection automatique de vocabulaire pour les films
def requete_info_movie(uri):
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


	response = requests.get(dbpedia_endpoint, params = payload)

	
	if(response.status_code==200):
		response_json = response.json()
		
		graphe = response_json['results']['bindings'][0]
		
		return graphe
	else:
		return []
	
		
#Requête qui alimente le graphe d'une page, pour chaque URI qu'elle contient
def requete_page(uri):
# Requête SPARQL
	payload = {
		"query": """SELECT DISTINCT (<"""+uri+"""> as ?s) ?p ?o
					WHERE {
						
						<"""+uri+"""> ?p ?o.
						
					} LIMIT """+nombre_liens_par_URI
					,
		"format": "json",
		"timeout": "30000"
	}


	response = requests.get(dbpedia_endpoint, params = payload)

	
	if(response.status_code==200):
		response_json = response.json()
		
		graphe = response_json['results']['bindings']
		
		return graphe
	else:
		return []
		
		
#Recherche des films en relation avec l'URI dans DBPedia
def cherche_films(uri):
# Requête SPARQL	

	payload = {
		"query": """SELECT DISTINCT ?s
					WHERE {
						
						?s a <http://dbpedia.org/ontology/Film>.
						?s ?p <"""+ uri +""">.
						
					} LIMIT """+nombre_films_DBPedia
					,
		"format": "json",
		"timeout": "30000"
	}

	response = requests.get(dbpedia_endpoint, params=payload)
	
	if(response.status_code == 200):
		response_json = response.json()
		
		films_URI = []
		

		try:
			for film in response_json['results']['bindings']:
				node = construit_graphe_film(film["s"]["value"])
				if node["infos"] is not []:
					films_URI.append(node)
		except:
			return []
			
			
		return films_URI
	else:
		return {}
		
		
#Recherche des films en relation avec l'URI dans notre graphe
def cherche_filmsAlternatif(uri):

	qres = graphe_alternatif.query(
		"""SELECT DISTINCT ?s
		   WHERE {
		   ?s ?p <"""+ uri +""">.
		   }LIMIT """ + nombre_films_alternatif)

	films_URI = []

	try:
		for s in qres:
			films_URI.append(construit_graphe_film(s[0]))
		
	except:
		return []
	
	return films_URI	
		
		
#Recherche des informations dans DBPedia à propos de uriFilm
def requete_film(uriFilm):
# Requête SPARQL	


	payload = {
		"query": """SELECT DISTINCT (<"""+uriFilm+"""> as ?s) ?p ?o
					WHERE {
						
						
						<"""+uriFilm+"""> ?p ?o.
						
					} LIMIT	"""+nombre_liens_films_DBPedia
					,
		"format": "json",
		"timeout": "30000"
	}
	

	response = requests.get(dbpedia_endpoint, params = payload)
	
	if(response.status_code==200):
		response_json = response.json()
		
		return response_json['results']['bindings']
	else:
		return {}
		
		
#Recherche des informations dans notre graphe à propos de uriFilm
def requete_film_alternative(uriFilm):
# Requête SPARQL	

	qres = graphe_alternatif.query(
		"""SELECT DISTINCT (<"""+uriFilm+"""> as ?s) ?p ?o
		   WHERE {
		   <"""+uriFilm+"""> ?p ?o.
		   }LIMIT 10""" + nombre_liens_films_alternatif)

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
	json_object = json.loads(jsonContent)


	for page in json_object["pages"]:
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
			struct['results']['graphePage']+=requete_page(uri)
			struct["results"]["films"]+=cherche_films(uri)
			struct["results"]["films"]+=cherche_filmsAlternatif(uri)
			

		sortie.append(struct)

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
		nombre_liens_par_URI = sys.argv[1]
	else:
		nombre_liens_par_URI = '50'
	if(2 < len(sys.argv)):
		nombre_films_DBPedia = sys.argv[2]
	else:
		nombre_films_DBPedia = '5'

	if(3 < len(sys.argv)):
		nombre_films_alternatif = sys.argv[3]
	else:
		nombre_films_alternatif = '10'
		
	if(4 < len(sys.argv)):
		nombre_liens_films_DBPedia = sys.argv[4]
	else:
		nombre_liens_films_DBPedia = '100'
		
	if(5 < len(sys.argv)):
		nombre_liens_films_alternatif = sys.argv[5]
	else:
		nombre_liens_films_alternatif = '100'
	if(6 < len(sys.argv)):
		nombre_liens_films_alternatif = sys.argv[6]
	else:
		nombre_films_mots_clefs = '10'

	if not os.path.isdir("sample_output"):
		os.mkdir(cache_dir)
	with open(output_file_name, "r") as myfile:
		json = myfile.read()
		print(main(json))