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
		listeFilms= dict()
		listeDescFilms = dict()
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
			totalMovie = 0
			for uri in dictionnary[url["link"]]: 
					totalMovie  = totalMovie + dictionnary[movie["link"]][uri]*dictionnary[url["link"]][uri]
			
					
			sumUrl = sum(dictionnary[url["link"]].values())
			sumMovie = sum(dictionnary[movie["link"]].values())
			totalDiv = sumUrl*sumMovie
			coeff = totalMovie / totalDiv
			print(str(totalMovie) +" total movie "+str(totalDiv))	
			listeFilms[movie["link"]] = coeff;
			listeDescFilms[movie["link"]]=movie
			del movie["graphe"]
		

		arraySorted = sorted(listeFilms.items(), key=operator.itemgetter(1), reverse=True)#sort to get the 3 best movies
		
		i=0;
		films = list();
		
		
		while (i<3 and i<len(arraySorted)) :
			
			films.append({"movie":listeDescFilms[arraySorted[i][0]], "coeff":arraySorted[i][1]})
			i=i+1
		nodes.append({ "link" : url["link"], "results":{"films":films}})
			
		

		
	return nodes		
		                         
                            

if __name__ == "__main__":


	with open ("exampleRDF.json", "r") as myfile:
    		data=myfile.read().replace('\n', '')
	
    		print(json.dumps(main(data)))




















