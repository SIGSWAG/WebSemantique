import json
import sets

# Reading data back
with open('exampleRDF.json', 'r') as f:
	 data = json.load(f)

'''for i in data["results"]["bindings"] :
	print(i["s"]["value"])   '''

dictionnary = dict()
dictionnary["total"]=set()

for url in data :
	dictionnary[url["link"]]=set()
	for uri in url["results"] :
		dictionnary["total"].add(uri["s"]["value"])
		dictionnary[url["link"]].add(uri["s"]["value"])
		if uri["o"]["type"] == "uri" :
			dictionnary["total"].add(uri["o"]["value"])
			dictionnary[url["link"]].add(uri["o"]["value"])
	print(url["link"])


totalCount = len(dictionnary["total"])

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
			print(url["link"]+"---"+str(len(inters))+"-->"+url1["link"])

result = {'nodes' : nodes, 'links' : links}

# Writing JSON data
#with open('resultGraph.json', 'w') as f:
#     json.dump(result, f)

print(json.dumps(result))		
		

