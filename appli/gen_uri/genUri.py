from gen_uri.bing_search_api import BingSearchAPI
import xml.etree.ElementTree
import requests, sys, json, os
import getopt

directory = 'gen_uri'
googleAPIKey = "AIzaSyB23UnDXR2PyYdSygH1ClmUvIHvrdwacDo"
searchEngineKey = "016723847753961302155:y6-cneh1knc"
googleSearchURL = "https://www.googleapis.com/customsearch/v1"
googleSearchExampleFile = os.path.join(directory, "exampleResponse.json")

bingSearchAPIKey = "mX9yeDnqzockohCH18xBGKH1P/78ESUIpR08YB0zSAo"
bingSearchURL = "https://api.datamarket.azure.com/Bing/Search/Web"

dbpediaSpotlightURL = "http://spotlight.dbpedia.org/rest/annotate"
spotlightExampleFile = os.path.join(directory, "spotlightResponseExample.xml")

'''
============================================================================
PART 1 : Send a query and retrieve list of URLs
============================================================================
'''

def getURLSfromQuery(query):

  #jsonContent = getSearchFromGoogleCSE(query, True)
  jsonContent = getSearchFromFile()

  jsonObject = json.loads(jsonContent)

  urls = []
  for item in jsonObject['items']:
    print(item['link'])
    urls.append(item['link'])

  return urls;

def getSearchFromFile():
  with open(googleSearchExampleFile, "r") as myfile:
    jsonContent = myfile.read()

  return jsonContent

def getSearchFromGoogleCSE(query, writeToFile):
  payload = {
    "query": query,
    "key": googleAPIKey,
    "cx": searchEngineKey
  }

  response = requests.get(googleSearchURL, params=payload)
  jsonContent = response.json()

  if(writeToFile):
    writeContentToFile(googleSearchExampleFile, jsonContent)

  return jsonContent

def getSearchFromBing(query, writeToFile):
  api = BingSearchAPI(bingSearchAPIKey)
  params = {'$format': 'json'}
  jsonContent =  api.search_web(query, payload=params)

  if(writeToFile):
    writeContentToFile(googleSearchExampleFile, jsonContent)

  return jsonContent


def writeContentToFile(fileName, content):
  with open(fileName, "w") as jsonFile:
    jsonFile.write(content)

'''
============================================================================
PART 2 : For each URL, use Alchemy to extract text and semantic data
============================================================================
'''


'''
============================================================================
PART 3 : For each snippet of text, enhance with DBpedia Spotlight (annotate)
============================================================================
'''

def getURIsFromTexts(texts, spotlightConfidence, spotlightSupport):
  annotatedTexts = {}
  for url, text in texts.items():
    uris = getURIsFromText(text, spotlightConfidence, spotlightSupport)
    annotatedTexts[url] = uris

  return annotatedTexts

def getURIsFromText(text, spotlightConfidence, spotlightSupport):
  
  content = getAnnotatedTextFromSpotlight(text, spotlightConfidence, spotlightSupport, None)
  #content = getAnnotatedTextFromFile()

  # Extract URI
  uris = getDBPediaRessources(content)

  return uris

def getAnnotatedTextFromFile():
  with open(spotlightExampleFile, "r") as myfile:
    content = myfile.read()

  return content


def getAnnotatedTextFromSpotlight(text, spotlightConfidence, spotlightSupport, writeToFile):
  payload = {
    "text": text,
    "confidence": spotlightConfidence,
    "support": spotlightSupport
    #"sparql":
  }

  response = requests.get(dbpediaSpotlightURL, params=payload)

  content = response.text
    
  if(writeToFile):
    writeContentToFile(spotlightExampleFile, content)

  return content

def getDBPediaRessources(xmlRawContent):
  xmlRoot = xml.etree.ElementTree.fromstring(xmlRawContent)
  xmlRoot = xmlRoot.find("Resources")
  resources = xmlRoot.findall("Resource")
  
  uris = []
  for resource in resources:
    uri = resource.get("URI")
    uris.append(uri)

  return uris


'''
============================================================================
MAIN
============================================================================
'''

def main(keywords, spotlightConfidence, spotlightSupport):
  # Retrieve URLS based on query
  urls = getURLSfromQuery(keywords)

  # Retrieve, for each URL, an associated text
  texts = {
      urls[0]: "Paroled labor racketeer Dapper Dino is sought after by a politically ambitious prosecutor schemes to put him back in jail and a deceitful partner sizes him up for concrete shoes."
  }

  # Retrieve, for each text, the list of corresponding URIs
  annotatedTexts = getURIsFromTexts(texts, spotlightConfidence, spotlightSupport)


  # Prepare the JSON
  response = []
  for url, uris in annotatedTexts.items():
    response.append({
        "url": url,
        "uri": uris
      })

  jsonResponse = json.dumps(response)
  return(jsonResponse)


if  __name__ =='__main__':
  main("test", 0.2, 20)