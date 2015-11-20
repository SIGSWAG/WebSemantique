#!/usr/bin/python3
import sys, getopt
import subprocess
import os


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
	return mots_clefs, seuil_jordan


def main(argv):
	keywords, seuil_jordan = get_params(argv)
	## récupération des URIs
	os.chdir('gen_uri')
	from gen_uri import genUri
	json_uris = genUri.main(keywords, 0.2, 20)
	os.chdir('..')
	## récupération des RDFs
	os.chdir('sparql')
	from sparql import sparql
	json_rdfs = sparql.main(json_uris)
	os.chdir('..')
	## récupèration du graphe
	os.chdir('gen_graph')
	from gen_graph import genGraph
	output = genGraph.main(json_rdfs)
	os.chdir('..')
	## final output
	print(output)


if __name__ == "__main__":
	main(sys.argv[1:])

