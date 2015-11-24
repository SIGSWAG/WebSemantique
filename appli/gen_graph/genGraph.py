import json
import sys
import operator 


def main(jsonString):
	data=json.loads(jsonString)

	dictionnary = dict()
	dictionnary["total"]=set()


	urls = list()
	nodes = list()

	for url in data :
		listeFilms= dict()
		listeDescFilms = dict()
		dictionnary[url["link"]]=set()
		for uri in url["results"]["graphePage"]:
			# print(uri["s"])
			dictionnary[url["link"]].add(uri["s"]["value"])
			if uri["o"]["type"] == "uri" :
				dictionnary[url["link"]].add(uri["o"]["value"])
		# print(url["link"]+" tot "+str(len(dictionnary[url["link"]])))
		for movie in url["results"]["films"]:
			dictionnary[movie["link"]]=set()
			for uri in movie["graphe"] :
				dictionnary[movie["link"]].add(uri["s"]["value"])
				if uri["o"]["type"] == "uri" :
					dictionnary[movie["link"]].add(uri["o"]["value"])
		#calculate here jaccard for the movie
			# print(movie["link"]+" "+str(len(dictionnary[movie["link"]])))
			inters = dictionnary[movie["link"]].intersection(dictionnary[url["link"]])
			union = dictionnary[movie["link"]].union(dictionnary[url["link"]])
			coeff = len(inters)/len(union)
			listeFilms[movie["link"]] = coeff;
			listeDescFilms[movie["link"]]=movie
		arraySorted = sorted(listeFilms.items(), key=operator.itemgetter(1), reverse=True)#sort to get the 3 best movies
		
		i=0;
		films = list();
		
		
		while (i<3 and i<len(arraySorted)) :
			# print(arraySorted[i])
			films.append({"movie":listeDescFilms[arraySorted[i][0]], "coeff":arraySorted[i][1]})
			i=i+1
		nodes.append({ "link" : url["link"], "results":{"graphePage":url["results"]["graphePage"], "films":films}})
			
		#get the 3 best movies corresponding now
			
		
	
		
		#print(url["link"])


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
	return json.dumps(nodes)


if __name__ == "__main__":
	with open (os.path.join("sample_output","exampleRDF.json"), "r") as myfile:
		data=myfile.read().replace('\n', '')
		print(json.dumps(main(data)))

