#!/usr/bin/python3

import os
import cgi
import sys
sys.path.append(os.path.abspath(os.path.join('..', 'appli')))

os.chdir('..')
os.chdir('appli')
import main

print("Content-Type: application/json")  # JSON is following.
print()

arguments = cgi.FieldStorage()
if 'max_number_of_results' in arguments and	'mots_clefs' in arguments and 'search_type' in arguments and 'spotlight_confidence' in arguments and 'from_web' in arguments and 'spotlight_support' in arguments and 'append_keyword' in arguments:
	response = main.main([
						 '-m', arguments.getvalue('mots_clefs')
						,'-r', arguments.getvalue('max_number_of_results')
						,'-t', arguments.getvalue('search_type')
						,'-c', arguments.getvalue('spotlight_confidence')
						,'-f', arguments.getvalue('from_web')
						,'-s', arguments.getvalue('spotlight_support')
						,'-a', arguments.getvalue('append_keyword')
						])
	print(response)
else:
	print('7 parametres necessaires : "max_number_of_results", "mots_clefs", "search_type", "spotlight_confidence", "from_web", "spotlight_support", "append_keyword"')
