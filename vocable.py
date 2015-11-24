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

	'''totalCount = len(dictionnary["total"])
	nodes = list()
	for url in data :
		nodes.append({ 'name' : url["link"] })
	links = list()
	for i, url in enumerate(data) :
		for j, url1 in enumerate(data) :
			if url != url1 and j >= i : # Remove already computed links
				inters = dictionnary[url["link"]].intersection(dictionnary[url1["link"]])
				val = len(inters) / totalCount
				if val > 0 :
					res=dict()
					res["source"]=i
					res["target"]=j
					res["val"]=val
					links.append(res)
				#print(url["link"]+"---"+str(len(inters))+"-->"+url1["link"])
	result = {'nodes' : nodes, 'links' : links}
		'''
	return result		
		                         
                            

if __name__ == "__main__":
	with open ("vocabFilms.json", "r") as myfile:
    		vocabFilms=myfile.read().replace('\n', '')
	with open ("vocab.json", "r") as myfile:
    		vocabGeneral=myfile.read().replace('\n', '')
	
    		print(json.dumps(main(vocabFilms,vocabGeneral)))




