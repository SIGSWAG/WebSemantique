#!/usr/bin/python3
import os
import cgi
import sys
sys.path.append(os.path.abspath('../appli'))
import main


arguments = cgi.FieldStorage()
os.chdir('..')
os.chdir('appli')
print("Content-Type: application/json")  # JSON is following.
print()

if 'max_number_of_results' in arguments and	'mots_clefs' in arguments and 'search_type' in arguments and 'spotlight_confidence' in arguments and 'from_web' in arguments and 'spotlight_support' in arguments :
	response = main.main([
						 '-m', arguments.getvalue('mots_clefs')
						,'-r', arguments.getvalue('max_number_of_results')
						,'-t', arguments.getvalue('search_type')
						,'-c', arguments.getvalue('spotlight_confidence')
						,'-f', arguments.getvalue('from_web')
						,'-s', arguments.getvalue('spotlight_support')
						])
	print(response)
else:
	print('5 parametres necessaires : "max_number_of_results", "mots_clefs", "search_type", "spotlight_confidence", "from_web"')

