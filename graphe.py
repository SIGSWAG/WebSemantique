import json
import sets

# Reading data back
with open('exampleRDF.json', 'r') as f:
     data = json.load(f)
     
'''for i in data["results"]["bindings"] :
	print(i["s"]["value"])   '''
     
totalCount =  0

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


print(str(len(dictionnary["total"])))


result=list()


for url in data :
	for url1 in data :
			inters = dictionnary[url["link"]].intersection(dictionnary[url1["link"]])

			res=dict()
			res["URL1"]=url["link"]
			res["URL2"]=url1["link"]
			res["val"]=len(inters)
			result.append(res)
			print(url["link"]+"---"+str(len(inters))+"-->"+url1["link"])
			
# Writing JSON data
#with open('resultGraph.json', 'w') as f:
#     json.dump(result, f)

print(json.dumps(result))		
		
