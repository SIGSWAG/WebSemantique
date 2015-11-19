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
	mots_clefs, seuil_jordan = get_params(argv)
	## récupération des URIs
	os.chdir('gen_uri')
	uri_process_cmd = get_cmd()
	uri_process_cmd.append('--mots_clefs={mots_clefs}'.format(mots_clefs=mots_clefs))
	uri_process = subprocess.Popen(
							uri_process_cmd
							,stdout=subprocess.PIPE)
	os.chdir('..')
	## récupération des RDFs
	os.chdir('sparql')
	sparql_process = subprocess.Popen(
							get_cmd()
							,stdin=uri_process.stdout
							,stdout=subprocess.PIPE)
	uri_process.stdout.close()
	os.chdir('..')
	## récupèration du graphe
	os.chdir('gen_graph')
	graph_process = subprocess.Popen(
							get_cmd()
							,stdin=sparql_process.stdout
							,stdout=subprocess.PIPE)
	uri_process.stdout.close()
	os.chdir('..')
	## final output
	output = graph_process.communicate()[0].decode("utf-8")
	print(output)


if __name__ == "__main__":
	main(sys.argv[1:])

