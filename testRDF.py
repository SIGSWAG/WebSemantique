import rdflib, json

g = rdflib.Graph()
g.parse("baseAlternative.rdf", format="nt")


qres = g.query(
    """SELECT DISTINCT *
       WHERE {
	   ?s ?p ?o.
       }""")


graphe = []
	
for s, p, o in qres:
    
	lien = {}
	lien["s"]={}
	lien["s"]["value"]=s
	lien["s"]["type"]="uri"
	lien["p"]={}
	lien["p"]["value"]=p
	lien["p"]["type"]="uri"
	lien["o"]={}
	lien["o"]["value"]=o
	lien["o"]["type"]="uri"
	graphe.append(lien)
	
with open("jacky.txt", "w") as myfile:
		myfile.write(json.dumps(graphe))
	
#print(qres.serialize(format='json-ld', indent=4))