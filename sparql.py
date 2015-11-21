import requests, sys, json

def main():

    dbpediaEndpoint = "http://live.dbpedia.org/sparql"
    inputURIs = "sample.json"
    outputFileName = "output.json"

    # Lecture des URIs

    with open(inputURIs, "r") as myfile:
        jsonContent = myfile.read()
    jsonObject = json.loads(jsonContent)

    for uri in jsonObject["uris"]:
        print(uri["url"] + " --- " + str(uri["uri"]))


    # Requête SPARQL

    payload = {
        "query": """SELECT DISTINCT *
                    WHERE {
                        ?film rdf:type <http://dbpedia.org/ontology/Film> .
                        ?film ?prop ?propval
                    } LIMIT 250
                    OFFSET 5000""",
        "format": "json",
        "timeout": "30000"
    }

    response = requests.get(dbpediaEndpoint, params = payload)
    responseJson = json.loads(response.text)

    # TODO transformer le JSON dans le format approprié

    with open(outputFileName, "w") as myfile:
        myfile.write(json.dumps(responseJson))

main()
