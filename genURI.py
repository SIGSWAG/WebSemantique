from bing_search_api import BingSearchAPI
import xml.etree.ElementTree, requests, sys, json

googleAPIKey = "AIzaSyB23UnDXR2PyYdSygH1ClmUvIHvrdwacDo"
searchEngineKey = "016723847753961302155:y6-cneh1knc"
googleSearchURL = "https://www.googleapis.com/customsearch/v1"
googleSearchExampleFile = "exampleResponse.json"

bingSearchAPIKey = "mX9yeDnqzockohCH18xBGKH1P/78ESUIpR08YB0zSAo"
bingSearchURL = "https://api.datamarket.azure.com/Bing/Search/Web"

dbpediaSpotlightURL = "http://spotlight.dbpedia.org/rest/annotate"
spotlightExampleFile = "spotlightResponseExample.xml"

'''
============================================================================
PART 1 : Send a query and retrieve list of URLs
============================================================================
'''

def getURLSfromQuery(query, maxNumberOfResults, fromWeb):
  urls = []

  # If we need to do a real request on the web
  if(fromWeb):
    # Get the number of requests (10 results per request)
    numberOfRequests = maxNumberOfResults // 10
    # Get the number of results to return for the last request
    lastOffset = maxNumberOfResults % 10

    for offset in range(0, numberOfRequests):
      jsonContent = getSearchFromGoogleCSE(query, (offset*10), True)
      addUrlToList(urls, jsonContent)

    if(lastOffset != 0):
      jsonContent = getSearchFromGoogleCSE(query, (offset*10) + lastOffset, True)
      addUrlToList(urls, jsonContent)
  else:
    jsonContent = getSearchFromFile()
    addUrlToList(urls, jsonContent)

  return urls

def addUrlToList(urls, jsonContent):
  jsonObject = json.loads(jsonContent)
  
  for item in jsonObject['items']:
    print(item['link'])
    urls.append(item['link'])

def getSearchFromFile():
  with open(googleSearchExampleFile, "r") as myfile:
    jsonContent = myfile.read()

  return jsonContent

def getSearchFromGoogleCSE(query, offset, writeToFile):
  payload = {
    "q": query,
    "fields": "items(link)",
    "key": googleAPIKey,
    "cx": searchEngineKey,
    #"lr": "lang_en",
    #"start": offset
  }

  response = requests.get(googleSearchURL, params = payload)
  jsonContent = response.text
  print(jsonContent)

  if(writeToFile):
    writeContentToFile(googleSearchExampleFile, jsonContent)

  return jsonContent

def getSearchFromBing(query, writeToFile):
  api = BingSearchAPI(bingSearchAPIKey)

  params = {
    "$format": "json"
  }

  jsonContent =  api.search_web(query, payload = params)

  if(writeToFile):
    writeContentToFile(googleSearchExampleFile, jsonContent)

  return jsonContent


def writeContentToFile(fileName, content):
  with open(fileName, "a+") as jsonFile:
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
    #"sparql": sparql
  }

  response = requests.get(dbpediaSpotlightURL, params = payload)

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

def main(query, maxNumberOfResults, spotlightConfidence, spotlightSupport):
  # Retrieve URLS based on query
  urls = getURLSfromQuery(query, maxNumberOfResults, True)

  # Retrieve, for each URL, an associated text
  texts = {
      urls[0]: "Paroled labor racketeer Dapper Dino is sought after by a politically ambitious prosecutor schemes to put him back in jail and a deceitful partner sizes him up for concrete shoes."
  }

  # Retrieve, for each text, the list of corresponding URIs
  annotatedTexts = getURIsFromTexts(texts, spotlightConfidence, spotlightSupport)

  # Prepare the JSON
  responseUriArray = []
  for url, uris in annotatedTexts.items():
    responseUriArray.append({
        "url": url,
        "uri": uris
      })

  response = {
    "uris": responseUriArray
  }

  jsonResponse = json.dumps(response)

  return jsonResponse

'''
========================================================================
Usage 
python genURI.py Inception 20 0.4 34
============================================================================
'''
if  __name__ =='__main__':

  query = sys.argv[1]

  # Number of results to return from queries 
  if(2 < len(sys.argv)):
    maxNumberOfResults = sys.argv[2]
  else:
    maxNumberOfResults = 20

  # Default values for spotlightConfidence is 0.2 and for spotlightSupport is 20
  if(3 < len(sys.argv)):
    spotlightConfidence = sys.argv[3]
  else:
    spotlightConfidence = 0.2

  if(4 < len(sys.argv)):
    spotlightSupport = sys.argv[4]
  else:
    spotlightSupport = 20

  jsonResponse = main(query, maxNumberOfResults, spotlightConfidence, spotlightSupport)

  print(jsonResponse)
