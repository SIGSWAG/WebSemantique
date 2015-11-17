import fileinput
import os


def main(ensemble_rtf):
	with open(os.path.abspath('sample_output/genGraph.txt')) as f:
		lines = f.read()
	return lines


if __name__ == "__main__":
	ensemble_rtf = ''
	for line in fileinput.input():
		ensemble_rtf += line
	print(main(ensemble_rtf))
