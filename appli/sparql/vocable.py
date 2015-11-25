import json
import sys
import operator 


def main(jsonStringMovies, jsonStringGeneral):                         
        
	dataMovies=json.loads(jsonStringMovies)
	dataGeneral=json.loads(jsonStringGeneral)
     
	dictionnary = dict()
	setGeneral =set()
	setMovies =set()
		
	result = list()

	for uri in dataGeneral["results"]["bindings"] :
		setGeneral.add(uri["p"]["value"])
	
	for uri in dataMovies["results"]["bindings"] :
		setMovies.add(uri["p"]["value"])	
		
	resultSet = setMovies.difference(setGeneral);	
	
	for uri in resultSet :
		result.append({"predicat": uri})

                            

if __name__ == "__main__":
	with open ("vocabFilms.json", "r") as myfile:
    		vocabFilms=myfile.read().replace('\n', '')
	with open ("vocab.json", "r") as myfile:
    		vocabGeneral=myfile.read().replace('\n', '')
	
    		print(json.dumps(main(vocabFilms,vocabGeneral)))




