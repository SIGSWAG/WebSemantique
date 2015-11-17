import requests, sys, json

googleAPIKey = "AIzaSyB23UnDXR2PyYdSygH1ClmUvIHvrdwacDo"
searchEngineKey = "016723847753961302155:y6-cneh1knc"

def getURLSfromQuery(query):

  #jsonContent = getJSONFromWeb(query)
  jsonContent = getJSONFromFile()

  jsonObject = json.loads(jsonContent)

  urls = []
  for item in jsonObject['items']:
    print(item['link'])
    urls.append(item['link'])

  return urls;

def getJSONFromFile():
  with open("exampleResponse.json", "r") as myfile:
    jsonContent = myfile.read()

  return jsonContent

def getJSONFromWeb(query):
  response = requests.get("https://www.googleapis.com/customsearch/v1?q=" + query + "&key=" + googleAPIKey + "&cx= " + searchEngineKey)
  jsonContent = response.json()

  writeJSONToFile(jsonContent)

  return jsonContent

def writeJSONToFile(json):
  with open("exampleResponse.json", "a") as jsonFile:
    jsonFile.write(json)

def main():
  query = sys.argv[1]
  getURLSfromQuery(query)

if  __name__ =='__main__':
  main()