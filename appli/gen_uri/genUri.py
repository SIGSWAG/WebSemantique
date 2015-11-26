from gen_uri.bing_search_api import BingSearchAPI
from gen_uri.alchemyapi import AlchemyAPI
from gen_uri.threadingRequests import *
from enum import Enum
import xml.etree.ElementTree, sys, re, requests, json, os, getopt

directory = 'gen_uri'
alchemyRootURL = "http://access.alchemyapi.com/calls"
alchemyTextSearchURL = "/url/URLGetText"
alchemyConceptSearchURL = "/url/URLGetRankedConcepts"
alchemyGetNews = "/data/GetNews"
alchemyAPIKey = "9d4bfa22ad347204f33e0451834cef0fe6f5b9e3"
alchemyAPIKeyRescue = "cf9f0b681c01368d7329c9c4277c9b7ea91e8732"
alchemyGetConceptsURL = "http://gateway-a.watsonplatform.net/calls/url/URLGetRankedConcepts"
alchemyGetConceptsTextURL = "http://gateway-a.watsonplatform.net/calls/text/TextGetRankedConcepts"
alchemyAPIKey = "cf9f0b681c01368d7329c9c4277c9b7ea91e8732"
alchemyAPIKeyRescueBis = "1c29f8e0024bf320f7974af9cbe6612ec1dd8d73"

googleAPIKey = "AIzaSyB23UnDXR2PyYdSygH1ClmUvIHvrdwacDo"
googleAPIKeyRescue = "AIzaSyA1CXFhP9LGmIFZokfkOjnU78Y32dRYWk0"
searchEngineKey = "016723847753961302155:y6-cneh1knc"
searchEngineKeyRescue = "001392524783232473057:uwxuk9qp0-a"
googleSearchURL = "https://www.googleapis.com/customsearch/v1"

googleSearchExampleFile = os.path.join(directory, os.path.join("sample_output", "exampleResponse.json"))
googleSearchesExampleFile = os.path.join(directory, os.path.join("sample_output", "exampleResponses.json"))

googleNbResultsPerRequest = 10

bingSearchAPIKey = "Qf4hLruRDq3/DICqgrhXPVQRlfrebkPCwI0Hd66EgmU"
bingSearchURL = "https://api.datamarket.azure.com/Bing/Search/Web"
bingSearchExampleFile = os.path.join(directory, os.path.join("sample_output", "bingResponse.json"))
bingNbResultsPerRequest = 50

dbpediaSpotlightURL = "http://spotlight.dbpedia.org/rest/annotate"
spotlightExampleFile = os.path.join(directory, os.path.join("sample_output", "spotlightResponseExample.xml"))

sampleOutput = os.path.join(directory, os.path.join("sample_output", "genUri.txt"))

appendKeywordMovie = "movie"
enableWritting = False

regexWhitespaces = re.compile(r'\s+')


class SearchType(Enum):
    GOOGLE_ONLY = 1
    BING_ONLY = 2
    GOOGLE_AND_BING = 3



'''
============================================================================
PART 1 : Send a query and retrieve list of URLs
============================================================================
'''
def getURLsfromQuery(query, maxNumberOfResults=100, searchType=SearchType.GOOGLE_ONLY, appendKeyword=False, fromWeb=False):
    if (maxNumberOfResults > 100):
        maxNumberOfResults = 100

    urls = []
    titles = {}

    # If we need to do a real request on the web
    if (fromWeb):
        if (appendKeyword):
            query += " " + appendKeywordMovie

        if (searchType == SearchType.GOOGLE_ONLY):
            getURLsFromGoogle(query, maxNumberOfResults, urls, titles)

        elif (searchType == SearchType.BING_ONLY):
            getURLsFromBing(query, maxNumberOfResults, urls, titles)

        elif (searchType == SearchType.GOOGLE_AND_BING):
            # Divide evenly the number of requests between the two search engines
            numberOfRequestsPerSearchEngine = maxNumberOfResults // 2
            # The remainder will be added to the number of requests of Bing (less restrictive than Google limit wise)
            lastOffsetToAddToBing = maxNumberOfResults % 2

            # Google
            getURLsFromGoogle(query, numberOfRequestsPerSearchEngine, urls, titles)

            # Bing
            getURLsFromBing(query, numberOfRequestsPerSearchEngine + lastOffsetToAddToBing, urls, titles)

        else:
            # Not a correct search engine, throw error ?
            numberOfRequests = maxNumberOfResults // bingNbResultsPerRequest
    else:
        jsonContent = getSearchFromFile()
        #print(jsonContent)
        addGoogleUrlToList(urls, titles, jsonContent)

    return urls, titles


def getURLsFromGoogle(query, maxNumberOfResults, urls, titles):
    if (maxNumberOfResults < googleNbResultsPerRequest):

        jsonContent = getSearchFromGoogleCSE(query, 1, maxNumberOfResults, True)
        if not addGoogleUrlToList(urls, titles, jsonContent):
            jsonContent = getSearchFromGoogleCSE(query, 1, maxNumberOfResults, True)
            addGoogleUrlToList(urls, titles, jsonContent)
    else:
        # Get the number of requests to do (10 results per request)
        numberOfRequests = maxNumberOfResults // googleNbResultsPerRequest
        # Get the number of results to return for the last request (remainder of division)
        lastOffset = maxNumberOfResults % googleNbResultsPerRequest

        for offset in range(0, numberOfRequests):
            jsonContent = getSearchFromGoogleCSE(query, (offset * googleNbResultsPerRequest) + 1,
                                                 googleNbResultsPerRequest, True)
            if not addGoogleUrlToList(urls, jsonContent):
                jsonContent = getSearchFromGoogleCSE(query, (offset * googleNbResultsPerRequest) + 1,
                                                 googleNbResultsPerRequest, True)
                addGoogleUrlToList(urls, titles, jsonContent)

        # If a last request is needed to retrieve the last few results as requested by user
        if (lastOffset != 0):
            jsonContent = getSearchFromGoogleCSE(query, (offset * googleNbResultsPerRequest) + lastOffset + 1,
                                                 googleNbResultsPerRequest, True)
            if not addGoogleUrlToList(urls, titles, jsonContent):
                jsonContent = getSearchFromGoogleCSE(query, (offset * googleNbResultsPerRequest) + lastOffset + 1,
                                                 googleNbResultsPerRequest, True)
                addGoogleUrlToList(urls, titles, jsonContent)

def getURLsFromBing(query, maxNumberOfResults, urls, titles):
    if (maxNumberOfResults < bingNbResultsPerRequest):
        jsonContent = getSearchFromBing(query, 0, maxNumberOfResults, True)
        addBingUrlToList(urls, titles, jsonContent)
    else:
        # Get the number of requests to do (50 results per request)
        numberOfRequests = maxNumberOfResults // bingNbResultsPerRequest
        # Get the number of results to return for the last request (remainder of division)
        lastOffset = maxNumberOfResults % bingNbResultsPerRequest

        offset = 0
        for offset in range(0, numberOfRequests):
            jsonContent = getSearchFromBing(query, (offset * bingNbResultsPerRequest), bingNbResultsPerRequest, True)
            addBingUrlToList(urls, titles, jsonContent)

        # If a last request is needed to retrieve the last few results as requested by user
        if (lastOffset != 0):
            jsonContent = getSearchFromBing(query, (offset * bingNbResultsPerRequest) + lastOffset,
                                            bingNbResultsPerRequest, True)
            addBingUrlToList(urls, titles, jsonContent)


def addGoogleUrlToList(urls, titles, jsonContent):
    jsonObject = json.loads(jsonContent)
    #print(jsonObject)
    if 'items' in jsonObject:
        for item in jsonObject['items']:
            #print(item['link'])
            link = item['link']
            urls.append(link)
            titles[link] = item['title']
        return True
    else:
        globals()['googleAPIKey'] = googleAPIKeyRescue
        globals()['searchEngineKey'] = searchEngineKeyRescue
        return False


def addBingUrlToList(urls, titles, jsonContent):
    jsonObject = json.loads(jsonContent)

    jsonObject = jsonObject['d']

    for result in jsonObject['results']:
        link = result['Url']
        #print(result['Url'])
        titles[link] = result['Title']
        urls.append(link)


def getSearchFromFile():
    with open(googleSearchExampleFile, "r") as myfile:
        jsonContent = myfile.read()

    return jsonContent


def getSearchFromGoogleCSE(query, offset=1, numberOfResults=googleNbResultsPerRequest, writeToFile=True):
    payload = {
        "q": query,
        "fields": "items(link,title)",
        "key": googleAPIKey,
        "cx": searchEngineKey,
        "lr": "lang_en",
        "start": offset,
        "num": numberOfResults
    }

    response = requests.get(googleSearchURL, params=payload)
    jsonContent = response.text
    # print(jsonContent)

    if (writeToFile):
        writeContentToFile(googleSearchExampleFile, jsonContent, True)
        writeContentToFile(googleSearchesExampleFile, jsonContent, False)

    return jsonContent


def getSearchFromBing(query, offset=0, numberOfResults=bingNbResultsPerRequest, writeToFile=True):
    api = BingSearchAPI(bingSearchAPIKey)
    language = quote('en-US')
    params = {
        "$format": "json",
        "$skip": offset,
        "Market": language,
        "$top": numberOfResults
    }

    jsonContent = api.search_web(query, payload=params)
    
    jsonContent = jsonContent.text

    if writeToFile:
        writeContentToFile(bingSearchExampleFile, jsonContent)

    return jsonContent

def quote(query):
    '''Quote query with sign(')'''
    if query.startswith('\'') is not True:
        query = '\'' + query 

    if query.endswith('\'') is not True:
        query = query + '\''         
    
    return query

def writeContentToFile(fileName, content, replace=False):
    if replace:
        flag = "w"
    else:
        flag = "a+"

    with open(fileName, flag) as jsonFile:
        jsonFile.write(content)


'''
============================================================================
PART 2 : For each URL, use Alchemy to extract text and semantic data
============================================================================
'''
# Renvoie le texte concatene des 30 premieres plus grandes lignes du texte retourne par alchemy
def getTextsFromUrls(urls):
    texts = {}
    tabResponses = makeAlchemyRequest(urls, alchemyTextSearchURL)
    i = 1
    fail = 0
    for url in urls:
        rawResponse = tabResponses[i]
        i += 1
        text = ""
        fail = 0
        if  rawResponse is not None :
            response = rawResponse
            if  response['status'] == 'OK' :
                text = str(response['text'].encode('ascii', errors='ignore'))
                text = cleanText(text, 30)
            else:
                text = ""
                fail+=1
        else:
            fail+=1
        texts[url] = text

    if fail==len(urls):
        globals()['alchemyAPIKey'] = alchemyAPIKeyRescue
        return getTextsFromUrls(urls)

    return texts

def makeAlchemyRequest(urls, alchemyEndpoint = alchemyTextSearchURL):
    params_list = []
    for url in urls:
        param = {}
        param['url'] = url
        param['apikey'] = alchemyAPIKey
        param['outputMode'] = 'json'
        param["linkedData"] = "1"
        params_list.append(param)

    p = RequestPool(alchemyRootURL + alchemyEndpoint, params_list)
    p.launch()
    tabResponses = p.getResults()
    return tabResponses

def cleanText(text, nbLinesMax):
    text = deleteSpaces(text)
    lignes = text.split("\\n")
    sorted(lignes, key=lambda x: (len(x)), reverse=True)
    ret = ''
    for i in range(0, min(nbLinesMax, len(lignes))):
        ret += lignes[i]
    return ret


def deleteSpaces(text):
    cleanText = ''
    prev = 'a'
    for i in text:
        if ((i == ' ' and prev != ' ') or i != ' '):
            cleanText += i
            prev = i
    return cleanText

def getConceptsFromAlchemyBIS(urls):
    concepts = []
    responses = makeAlchemyRequest(urls,alchemyConceptSearchURL)
    i=1
    for url in urls :
        response = responses[i]
        i+=1
        dbpediaConcepts = []
        if response is not None :
            if response['status'] == 'OK':
                responseConcepts = response['concepts']
                for concept in responseConcepts :
                    if 'dbpedia' in concept:
                        dbpediaConcepts.append(concept['dbpedia'])

        concepts.append({'url':url,'concepts':dbpediaConcepts})
    return concepts

def getConceptsFromAlchemyByTexts(texts):
    uris = {}
    for url, text in texts.items:
        uris[url] = getConceptsFromAlchemyByText(text)

    return uris


def getConceptsFromAlchemyByText(text):
    payload = {
        "text": url,
        "apikey": alchemyAPIKey,
        "outputMode": "json",
        "linkedData": "1"
    }

    response = requests.get(alchemyGetConceptsURL, params=payload)
    
    jsonContent = response.text

    jsonObject = json.loads(jsonContent)

    uris = []
    for uri in jsonObject['concepts']:
        if 'dbpedia' in uri:
            uris.append(uri['dbpedia'])

    return uris
'''
============================================================================
PART 3 : For each Alchemy text output, use Spotlight to find related URI
============================================================================
'''
def makeSpotlightRequests(texts, spotlightConfidence, spotlightSupport) :
    spotParams = []
    for url, text in texts.items():
        if text and not text.isspace():
            spotParam = prepareSpotlightRequest(text, spotlightConfidence, spotlightSupport)
            spotParams.append(spotParam)

    p = RequestPool(dbpediaSpotlightURL, spotParams)
    p.launch()
    return p.getResults()


def prepareSpotlightRequest(text, spotlightConfidence, spotlightSupport):
    payload = {
        "text": text,
        "confidence": spotlightConfidence,
        "support": spotlightSupport
        # "sparql": sparql
    }
    return payload;


def getConceptsFromAlchemy(url):
    payload = {
        "url": url,
        "apikey": alchemyAPIKey,
        "outputMode": "json",
        "linkedData": "1"
    }

    response = requests.get(alchemyGetConceptsURL, params=payload)
    
    jsonContent = response.text

    jsonObject = json.loads(jsonContent)

    uris = []
    for uri in jsonObject['concepts']:
        if 'dbpedia' in uri:
            uris.append(uri['dbpedia'])

    return uris


'''
def getURIsFromTexts(texts, spotlightConfidence, spotlightSupport, writeToFile=False):
    annotatedTexts = {}

    results = makeSpotlightRequests(texts,spotlightConfidence,spotlightSupport)

    for result in results:
        print(result)
    content = ""
    if writeToFile:
        writeContentToFile(spotlightExampleFile, content)

    return annotatedTexts
'''
def getURIsFromTexts(texts, spotlightConfidence, spotlightSupport):
    annotatedTexts = {}
    for url, text in texts.items():
        if text and not text.isspace():
            uris = getURIsFromText(text, spotlightConfidence, spotlightSupport)
            urisFromAlchemyConcepts = getConceptsFromAlchemy(url)
            uris += urisFromAlchemyConcepts
            annotatedTexts[url] = uris

    return annotatedTexts


def getURIsFromText(text, spotlightConfidence, spotlightSupport):
    content = getAnnotatedTextFromSpotlight(text, spotlightConfidence, spotlightSupport, None)
    # content = getAnnotatedTextFromFile()

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
        # "sparql": sparql
    }
    response = requests.post(dbpediaSpotlightURL, data=payload)

    content = response.text

    if writeToFile:
        writeContentToFile(spotlightExampleFile, content)

    return content


def getDBPediaRessources(xmlRawContent):
    xmlRoot = xml.etree.ElementTree.fromstring(xmlRawContent)
    if not xmlRoot:
        return []
    xmlRoot = xmlRoot.find("Resources")
    if not xmlRoot:
        return []
    # If there is no Resource tag, return empty araay
    if not xmlRoot.find('Resource'):
        return []

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
@fromWeb : if the search is done on the web or from a saved version of the request
============================================================================
'''
def main(query, maxNumberOfResults, searchType, spotlightConfidence, spotlightSupport, fromWeb, appendKeyword):
    # Retrieve URLS based on query
    (urls, titles) = getURLsfromQuery(query, maxNumberOfResults, searchType, appendKeyword, fromWeb)

    # Retrieve, for each URL, an associated text
    texts = getTextsFromUrls(urls)
  
    # Retrieve, for each text, the list of corresponding URIs
    annotatedTexts = getURIsFromTexts(texts, spotlightConfidence, spotlightSupport)

    # Prepare the JSON
    responseUriArray = []
    for url, uris in annotatedTexts.items():
        title = titles[url]
        responseUriArray.append({
            "url": url,
            "title": title,
            "uri": uris
        })

    response = {
        "pages": responseUriArray
    }

    jsonResponse = json.dumps(response)

    writeContentToFile(sampleOutput, jsonResponse)
    return jsonResponse


'''
=========================================================================================================
Usage 
python genURI.py Inception 20 all 0.4 34 True
python genURI.py query searchEngine numberOfResults spotlightConfidence spotlightSupport appendKeyword
=========================================================================================================
'''
if __name__ == '__main__':
    query = sys.argv[1]

    # Number of results to return from queries
    if (2 < len(sys.argv)):
        maxNumberOfResults = int(sys.argv[2])
    else:
        maxNumberOfResults = 20

    # Search engine on which to search results for
    if (3 < len(sys.argv)):
        if (sys.argv[3] == "google"):
            searchType = SearchType.GOOGLE_ONLY
        elif (sys.argv[3] == "bing"):
            searchType = SearchType.BING_ONLY
        elif (sys.argv[3] == "all"):
            searchType = SearchType.GOOGLE_AND_BING
        else:
            searchType = SearchType.GOOGLE_ONLY
    else:
        searchType = SearchType.GOOGLE_ONLY

    # Default values for spotlightConfidence is 0.2 and for spotlightSupport is 20
    if (4 < len(sys.argv)):
        spotlightConfidence = sys.argv[4]
    else:
        spotlightConfidence = 0.2

    if (5 < len(sys.argv)):
        spotlightSupport = sys.argv[5]
    else:
        spotlightSupport = 20

    if (6 < len(sys.argv)):
        appendKeyword = sys.argv[6]
    else:
        appendKeyword = False

    jsonResponse = main(query, maxNumberOfResults, searchType, spotlightConfidence, spotlightSupport, appendKeyword)

    print(jsonResponse)
