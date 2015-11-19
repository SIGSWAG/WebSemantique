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

if 'seuil_jordan' in arguments and 'mots_clefs' in arguments:
	main.main(['-m', arguments.getvalue('mots_clefs'), '-s', arguments.getvalue('seuil_jordan') ])
else:
	print('deux parametres necessaires : "seuil_jordan" et "mots_clefs"')

