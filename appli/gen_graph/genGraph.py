import json
import sys
import operator 


def main(jsonString):
	data=json.loads(jsonString)

	dictionnary = dict()
	nodes = list()

	for url in data :
		listeFilms= dict()
		listeDescFilms = dict()
		dictionnary[url["link"]]=set()
		for uri in url["results"]["graphePage"] :
			
			dictionnary[url["link"]].add(uri["s"]["value"])
			if uri["o"]["type"] == "uri" :
				dictionnary[url["link"]].add(uri["o"]["value"])
		for movie in url["results"]["films"]:
			
			dictionnary[movie["link"]]=set()
			for uri in movie["graphe"] :
				dictionnary[movie["link"]].add(uri["s"]["value"])
				if uri["o"]["type"] == "uri" :
					dictionnary[movie["link"]].add(uri["o"]["value"])
		#calculate here jaccard for the movie
			inters = dictionnary[movie["link"]].intersection(dictionnary[url["link"]])
			union = dictionnary[movie["link"]].union(dictionnary[url["link"]])
			coeff = len(inters)/len(union)
			listeFilms[movie["link"]] = coeff;
			listeDescFilms[movie["link"]]=movie
			del movie["graphe"]
		

		arraySorted = sorted(listeFilms.items(), key=operator.itemgetter(1), reverse=True)#sort to get the 3 best movies
		
		i=0;
		films = list();
		
		
		while (i<3 and i<len(arraySorted)) :
			films.append({"movie":listeDescFilms[arraySorted[i][0]], "coeff":arraySorted[i][1]})
			i=i+1
		nodes.append({ "link" : url["link"], "title": url["title"], "results":{"films":films}})
		
	return json.dumps(nodes)


if __name__ == "__main__":
	with open("exampleRDF.json", "r") as myfile:
    		data=myfile.read().replace('\n', '')
	
    		print(json.dumps(main(data)))
