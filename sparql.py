import requests

def main():

    dbpediaEndpoint = "http://dbpedia.org/sparql"

    payload = {
        "query": """SELECT DISTINCT ?Concept
                    WHERE {[] a ?Concept}
                    LIMIT 100""",
        "format": "application/sparql-results+json",
        "timeout": "30000"
    }

    response = requests.get(dbpediaEndpoint, params = payload)
    content = response.text

    print(content)

main()
