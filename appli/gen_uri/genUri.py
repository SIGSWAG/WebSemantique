import sys, getopt
import os


def main(mots_clefs):
	with open(os.path.abspath('sample_output/genUri.txt')) as f:
		lines = f.read()
	return lines


if __name__ == "__main__":
	mots_clefs = ''
	try:
		opts, args = getopt.getopt(sys.argv[1:],"m:",["mots_clefs="])
	except getopt.GetoptError:
		print('genUri.py -m "mots clefs"')
		sys.exit(2)
	for opt, arg in opts:
		if opt in ('-m', '--mots_clefs'):
			mots_clefs = arg
	print(main(mots_clefs))
