#!/usr/bin/python3
import sys, getopt
import subprocess
import os
import hashlib


def get_cmd():
	with open('run.txt') as cmd_f:
		cmd_list = cmd_f.read().split()
	return cmd_list


## récupère les paramètres depuis la ligne de commande.
## les params mots_clefs et seuil_jordan sont obligatoires
def get_params(argv):
	mots_clefs = ''
	seuil_jordan = -1
	try:
		opts, args = getopt.getopt(argv,"m:s:",["mots_clefs=", "seuil_jordan="])
	except getopt.GetoptError:
		print('main.py -m "mots clefs" -s 0.3')
		sys.exit(2)
	for opt, arg in opts:
		if opt in ('-m', '--mots_clefs'):
			mots_clefs = arg
		if opt in ('-s', '--seuil_jordan'):
			seuil_jordan = float(arg)
	if not mots_clefs:
		print("Vous devez au minimum renseigner un mot clef.")
		print('$ main.py -m "mots clefs" -s 0.3')
		sys.exit(3)
	if seuil_jordan < 0 or seuil_jordan > 1:
		print("Le seuil de jordan doit être entre 0 et 1.")
		print('$ main.py -m "mots clefs" -s 0.3')
		sys.exit(4)
	return mots_clefs.encode('utf-8'), seuil_jordan


def main(argv):
	keywords, seuil_jordan = get_params(argv)
	request_cached = hashlib.sha256(keywords).hexdigest()
	cache_dir = 'cache'
	output = ''
	cached_file_path = os.path.join(cache_dir,request_cached)
	if request_cached in os.listdir(cache_dir):
		for line in open(cached_file_path):
			output += line
	else:
		## récupération des URIs
		from gen_uri import genUri
		json_uris = genUri.main(keywords, 0.2, 20)
		## récupération des RDFs
		from sparql import sparql
		json_rdfs = sparql.main(json_uris)
		## récupèration du graphe
		from gen_graph import genGraph
		output = genGraph.main(json_rdfs)
		## on enregistre la requête
		with open(cached_file_path, 'w') as cached_file:
			cached_file.write(output)
	print(output)


if __name__ == "__main__":
	main(sys.argv[1:])

