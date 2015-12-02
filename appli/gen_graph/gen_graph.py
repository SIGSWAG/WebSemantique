import json
import sys
import operator 
import collections

def main(jsonString):                         
        
	data=json.loads(jsonString)
     
	dictionnary = dict()
	urls = list();
	nodes = list()

	for url in data :
		liste_films= dict()
		liste_desc_films = dict()
		dictionnary[url["link"]]= collections.Counter()
		for uri in url["results"]["graphePage"] :
			dictionnary[url["link"]][uri["s"]["value"]]=dictionnary[url["link"]][uri["s"]["value"]]+1
			if uri["o"]["type"] == "uri" :
				dictionnary[url["link"]][uri["o"]["value"]]=dictionnary[url["link"]][uri["o"]["value"]]+1
		
		for movie in url["results"]["films"]:
			dictionnary[movie["link"]]=collections.Counter()
			for uri in movie["graphe"] :
				dictionnary[movie["link"]][uri["s"]["value"]]=dictionnary[movie["link"]][uri["s"]["value"]]+1
				if uri["o"]["type"] == "uri" :
					dictionnary[movie["link"]][uri["o"]["value"]]=dictionnary[movie["link"]][uri["o"]["value"]]+1
		#calculate here jaccard for the movie
			total_movie = 0
			for uri in dictionnary[url["link"]]: 
				total_movie  = total_movie + dictionnary[movie["link"]][uri]*dictionnary[url["link"]][uri]
			
					
			sum_url = sum(dictionnary[url["link"]].values())
			sum_movie = sum(dictionnary[movie["link"]].values())
			total_div = sum_url*sum_movie
			# handle x/0
			try:
				coeff = total_movie / total_div
			except:
				coeff = 0
			liste_films[movie["link"]] = coeff;
			liste_desc_films[movie["link"]]=movie
			del movie["graphe"]
		

		array_sorted = sorted(liste_films.items(), key=operator.itemgetter(1), reverse=True)#sort to get the 3 best movies
		
		i=0;
		films = list();
		
		
		while (i<3 and i<len(array_sorted)) :
			films.append({"movie":liste_desc_films[array_sorted[i][0]], "coeff":array_sorted[i][1]})
			i=i+1
		nodes.append({ "link" : url["link"], "title": url["title"], "results":{"films":films}})
		
	return json.dumps(nodes)


if __name__ == "__main__":
	with open ("exampleRDF.json", "r") as myfile:
		data=myfile.read().replace('\n', '')
		print(json.dumps(main(data)))

