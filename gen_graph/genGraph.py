import sys, getopt
import os

def main(ensemble_rdf):
	with open(os.path.abspath('sample_output/genGraph.txt')) as f:
		lines = f.read()
	return lines

if __name__ == "__main__":
	f = ''
	try:
		opts, args = getopt.getopt(sys.argv[1:],"f:",["file="])
	except getopt.GetoptError:
		print('main.py -f "file/with/graph/as/json"')
		sys.exit(2)
	for opt, arg in opts:
		if opt in ('-f', '--file'):
			f = arg
	with open(f) as file_ensemble_rdf:
		ensemble_rdf = file_ensemble_rdf.read()
	print(main(ensemble_rdf))
