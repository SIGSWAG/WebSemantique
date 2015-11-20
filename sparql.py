import requests, sys, json

def main():

    dbpediaEndpoint = "http://dbpedia.org/sparql"
    inputURIs = "sample.json"


    # Lecture des URIs

    with open(inputURIs, "r") as myfile:
        jsonContent = myfile.read()
    jsonObject = json.loads(jsonContent)

    for uri in jsonObject["uris"]:
        print(uri["url"] + " --- " + str(uri["uri"]))


    # Requête SPARQL

    payload = {
        "query": """SELECT DISTINCT ?Concept
                    WHERE {[] a ?Concept}
                    LIMIT 100""",
        "format": "json",
        "timeout": "30000"
    }

    response = requests.get(dbpediaEndpoint, params = payload)
    content = response.text

    print(content)

main()
