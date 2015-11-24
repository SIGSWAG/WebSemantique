#!/usr/bin/python3
import sys, getopt
import subprocess
import os
import hashlib
from gen_uri import genUri
from sparql import sparql
from gen_graph import genGraph


class Params(object):
	def __init__(self, mots_clefs, max_number_of_results, search_type, spotlight_confidence, from_web, spotlight_support, append_keyword):
		self.mots_clefs = mots_clefs
		self.mots_clefs_hash = (mots_clefs + "&é6,;").encode('utf-8')
		self.max_number_of_results = max_number_of_results
		self.max_number_of_results_hash = (str(max_number_of_results) + "&éàç").encode('utf-8')
		self.search_type = search_type
		self.search_type_hash = (str(search_type) + "#`é98;").encode('utf-8')
		self.spotlight_confidence = spotlight_confidence
		self.spotlight_confidence_hash = (str(spotlight_confidence) + "&é)ç{").encode('utf-8')
		self.spotlight_support = spotlight_support
		self.spotlight_support_hash = (str(spotlight_support) + "è8_|=)").encode('utf-8')
		self.from_web = from_web
		self.from_web_hash = (str(from_web) + "mT\ç{").encode('utf-8')
		self.append_keyword = append_keyword
		self.append_keyword_hash = (str(append_keyword) + "5@ç9^").encode('utf-8')


def get_cmd():
	with open('run.txt') as cmd_f:
		cmd_list = cmd_f.read().split()
	return cmd_list


## récupère les paramètres depuis la ligne de commande.
## les params mots_clefs et max_number_of_results sont obligatoires
def get_params(argv):
	mots_clefs = ''
	max_number_of_results = -1
	search_type = -1
	spotlight_confidence = -1
	spotlight_support = ''
	from_web = None
	append_keyword = None
	try:
		opts, args = getopt.getopt(argv,"m:r:t:c:f:s:a:",["mots_clefs=", "max_number_of_results=", "search_type=", "spotlight_confidence=", "from_web=", "spotlight_support=", "append_keyword="])
	except getopt.GetoptError:
		print('$ main.py -m "mots clefs" -r 10 -s 1 -c 0.1 -f false -a true')
		sys.exit(2)
	for opt, arg in opts:
		if opt in ('-m', '--mots_clefs'):
			mots_clefs = arg
		if opt in ('-r', '--max_number_of_results'):
			max_number_of_results = int(arg)
		if opt in ('-t', '--search_type'):
			search_type = genUri.SearchType(int(arg))
		if opt in ('-c', '--spotlight_confidence'):
			spotlight_confidence = float(arg)
		if opt in ('-f', '--from_web'):
			if arg == "true":
				from_web = True
			elif arg == "false":
				from_web = False
		if opt in ('-s', '--spotlight_support'):
			spotlight_support = arg
		if opt in ('-a', '--append_keyword'):
			if arg == "true":
				append_keyword = True
			elif arg == "false":
				append_keyword = False
	if not mots_clefs:
		print("Vous devez au minimum renseigner un mot clef.")
		print('$ main.py -m "mots clefs" -r 10 -s 1 -c 0.1 -f false -a true')
		sys.exit(3)
	if max_number_of_results < 1 or max_number_of_results > 100:
		print("Le nombre maximum de requêtes doit être entre 1 et 100.")
		print('$ main.py -m "mots clefs" -r 10 -s 1 -c 0.1 -f false -a true')
		sys.exit(4)
	if not search_type in [s for s in genUri.SearchType]:
		print("Le type de requête doit être entre compris entre 1 et 3 : 1=google, 2=bing, 3=les deux")
		print('$ main.py -m "mots clefs" -r 10 -s 1 -c 0.1 -f false -a true')
		sys.exit(5)
	if spotlight_confidence < 0 or spotlight_confidence > 1:
		print("Le paramètre spotlight_confidence doit se situer entre 0 et 1")
		print('$ main.py -m "mots clefs" -r 10 -s 1 -c 0.1 -f false -a true')
		sys.exit(6)
	if from_web is None:
		print("Le paramètre from_web est obligatoire et doit valoir soit true soit false")
		print('$ main.py -m "mots clefs" -r 10 -s 1 -c 0.1 -f false -a true')
		sys.exit(7)
	if append_keyword is None:
		print("Le paramètre append_keyword est obligatoire et doit valoir soit true soit false")
		print('$ main.py -m "mots clefs" -r 10 -s 1 -c 0.1 -f false -a true')
		sys.exit(8)
	return Params(mots_clefs, max_number_of_results, search_type, spotlight_confidence, from_web, spotlight_support, append_keyword)


def main(argv):
	parametres_main = get_params(argv)
	request_cached = parametres_main.mots_clefs + '_' + hashlib.sha1(parametres_main.mots_clefs_hash + parametres_main.max_number_of_results_hash + parametres_main.search_type_hash + parametres_main.spotlight_confidence_hash + parametres_main.from_web_hash + parametres_main.append_keyword_hash).hexdigest()
	cache_dir = 'cache'
	output = ''
	cached_file_path = os.path.join(cache_dir,request_cached)
	if not os.path.isdir(cache_dir):
		os.mkdir(cache_dir)
	if request_cached in os.listdir(cache_dir):
		for line in open(cached_file_path):
			output += line
	else:
		## récupération des URIs
		json_uris = genUri.main(parametres_main.mots_clefs
								,parametres_main.max_number_of_results
								,parametres_main.search_type
								,parametres_main.spotlight_confidence
								,parametres_main.spotlight_support
								,parametres_main.from_web
								,parametres_main.append_keyword)
		## récupération des RDFs
		json_rdfs = sparql.main(json_uris)
		## récupèration du graphe
		output = genGraph.main(json_rdfs)
		## on enregistre la requête
		with open(cached_file_path, 'w') as cached_file:
			cached_file.write(output)
	return output


if __name__ == "__main__":
	response = main(sys.argv[1:])
	print(response)
