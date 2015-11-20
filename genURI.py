from bing_search_api import BingSearchAPI
from enum import Enum
from alchemyapi import AlchemyAPI
import xml.etree.ElementTree, requests, sys, json

googleAPIKey = "AIzaSyB23UnDXR2PyYdSygH1ClmUvIHvrdwacDo"
searchEngineKey = "016723847753961302155:y6-cneh1knc"
googleSearchURL = "https://www.googleapis.com/customsearch/v1"
googleSearchExampleFile = "exampleResponse.json"
googleNbResultsPerRequest = 10

bingSearchAPIKey = "mX9yeDnqzockohCH18xBGKH1P/78ESUIpR08YB0zSAo"
bingSearchURL = "https://api.datamarket.azure.com/Bing/Search/Web"
bingNbResultsPerRequest = 50

dbpediaSpotlightURL = "http://spotlight.dbpedia.org/rest/annotate"
spotlightExampleFile = "spotlightResponseExample.xml"

class SearchType(Enum): 
  GOOGLE_ONLY = 1
  BING_ONLY = 2
  GOOGLE_AND_BING = 3


'''
============================================================================
PART 1 : Send a query and retrieve list of URLs
============================================================================
'''

def getURLSfromQuery(query, maxNumberOfResults = 100, searchType = SearchType.GOOGLE_ONLY, fromWeb = None):
  if(maxNumberOfResults > 100):
    maxNumberOfResults = 100

  urls = []

  # If we need to do a real request on the web
  if(fromWeb):
    if(searchType == SearchType.GOOGLE_ONLY):
        # Get the number of requests to do (10 results per request)
        numberOfRequests = maxNumberOfResults // googleNbResultsPerRequest
        # Get the number of results to return for the last request (remainder of division)
        lastOffset = maxNumberOfResults % googleNbResultsPerRequest

        for offset in range(0, numberOfRequests):
          jsonContent = getSearchFromGoogleCSE(query, (offset*googleNbResultsPerRequest) + 1, True)
          addUrlToList(urls, jsonContent)

        if(lastOffset != 0):
          jsonContent = getSearchFromGoogleCSE(query, (offset*googleNbResultsPerRequest) + lastOffset + 1, True)
          addUrlToList(urls, jsonContent)

    elif(searchType == SearchType.BING_ONLY):
      numberOfRequests = maxNumberOfResults // bingNbResultsPerRequest
      lastOffset = maxNumberOfResults % bingNbResultsPerRequest
      for offset in range(0, numberOfRequests):
        jsonContent = getSearchFromBing(query, (offset*googleNbResultsPerRequest) + 1, True)
        # Add urls to list, but need special parser for bing

    elif(searchType == SearchType.GOOGLE_AND_BING):
      numberOfRequests = maxNumberOfResults // googleNbResultsPerRequest
    else:
      # Not a correct search engine
      numberOfRequests = maxNumberOfResults // bingNbResultsPerRequest


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

def getSearchFromGoogleCSE(query, offset = 1, writeToFile = True):
  payload = {
    "q": query,
    "fields": "items(link)",
    "key": googleAPIKey,
    "cx": searchEngineKey,
    "lr": "lang_en",
    "start": offset
  }

  response = requests.get(googleSearchURL, params = payload)
  print(response.url)
  jsonContent = response.text
  print(jsonContent)

  if(writeToFile):
    writeContentToFile(googleSearchExampleFile, jsonContent)

  return jsonContent

def getSearchFromBing(query, offset = 1, writeToFile = True):
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

#Renvoie le texte concatene des 30 premieres plus grandes lignes du texte retourne par alchemy
def getTextsFromUrls(urls) :
  alch_handle = AlchemyAPI()
  texts = {}
  for url in urls:
    response = alch_handle.text('url', url)
    if(response['status'] == 'OK'):
      text = str(response['text'].encode('ascii', errors='ignore'))
      text = cleanText(text,30)
    else:
      text = ''
    texts[url] = text
  return texts

def cleanText(text, nbLinesMax):
  text = deleteSpaces(text)
  lignes = text.split("\\n")
  sorted(lignes,key= lambda x:(len(x)),reverse=True)
  ret = ''
  for i in range(0,min(nbLinesMax,len(lignes))):
    ret += lignes[i]
  return ret

def deleteSpaces(text):
  cleanText = ''
  prev = 'a'
  for i in text:
    if((i==' ' and prev!=' ') or i!=' '):
      cleanText += i
      prev = i
  return cleanText

'''
============================================================================
PART 3 : For each snippet of text, enhance with DBpedia Spotlight (annotate)
============================================================================
'''

def getURIsFromTexts(texts, spotlightConfidence, spotlightSupport):
  annotatedTexts = {}
  for url, text in texts.items():
    if text and not text.isspace():
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
@query : A query (string)
@maxNumberOfResults : The number of results to return (integer) (max 100)
@searchType : The type of search (SearchType enum)
@spotlightConfidence : The confidence for Spotlight
@spotlightSupport : The support for Spotlight
============================================================================
'''

def main(query, maxNumberOfResults, searchType, spotlightConfidence, spotlightSupport):
  # Retrieve URLS based on query
  urls = getURLSfromQuery(query, maxNumberOfResults, searchType, True)

  # Retrieve, for each URL, an associated text
  texts = getTextsFromUrls(urls)
  
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
    "pages": responseUriArray
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

  jsonResponse = main(query, maxNumberOfResults, SearchType.GOOGLE_ONLY, spotlightConfidence, spotlightSupport)

  print(jsonResponse)
