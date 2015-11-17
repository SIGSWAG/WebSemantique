import sys, getopt
import os

def main(mots_clefs):
	with open(os.path.abspath('sample_output/genUri.txt')) as f:
		lines = f.read()
	return lines

if __name__ == "__main__":
	f = ''
	try:
		opts, args = getopt.getopt(sys.argv[1:],"f:",["file="])
	except getopt.GetoptError:
		print('main.py -f "file/with/all/uris"')
		sys.exit(2)
	for opt, arg in opts:
		if opt in ('-f', '--file'):
			f = arg
	with open(f) as file_mots_clefs:
		mots_clefs = file_mots_clefs.read()
	print(main(mots_clefs))