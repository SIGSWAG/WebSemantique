import fileinput
import os

def main(ensemble_uri):
	with open(os.path.abspath('sample_output/sparql.txt')) as f:
		lines = f.read()
	return lines

if __name__ == "__main__":
	ensemble_uri = ''
	for line in fileinput.input():
		ensemble_uri += line
	print(main(ensemble_uri))
