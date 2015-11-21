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
if 'seuil_jordan' in arguments and 'mots_clefs' in arguments:
	main.main(['-m', arguments.getvalue('mots_clefs'), '-s', arguments.getvalue('seuil_jordan') ])
else:
	print('deux parametres necessaires : "seuil_jordan" et "mots_clefs"')

