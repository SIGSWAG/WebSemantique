
import xml.etree.ElementTree, requests, sys, json

inputResumes = "resume.txt"
dbpediaSpotlightURL = "http://spotlight.dbpedia.org/rest/annotate"
spotlightExampleFile = "spotlightResponseExample.xml"


def writeContentToFile(fileName, content):
  with open(fileName, "w") as jsonFile:
    jsonFile.write(content)

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
	graphe = getDBPediaRessources(content)
	
	writeContentToFile(spotlightExampleFile, graphe)
	
		

	return graphe
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
	
	headers = {
		"Accept": "text/xml"
	}

	
	for i in range(0,9):
		response = requests.get(dbpediaSpotlightURL, headers = headers, params = payload)

		if(response.status_code==200):	
			
			content = response.content.decode('utf-8').encode('cp850','replace').decode('cp850')

			if(writeToFile):
				writeContentToFile(spotlightExampleFile, content)
			
			return content

	return 0

def getDBPediaRessources(xmlRawContent):
	xmlRoot = xml.etree.ElementTree.fromstring(xmlRawContent)
	xmlRoot = xmlRoot.find("Resources")
	resources = xmlRoot.findall("Resource")

	graphe = ""
	for resource in resources:
		lien = "film relationTheme " + resource.get("URI")
		graphe+=lien + '\n'
		
	return graphe
  
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

def main(spotlightConfidence, spotlightSupport):

  # Retrieve, for each URL, an associated text
	with open(inputResumes, "r") as myfile:
		text = myfile.read()
  
  # Retrieve, for each text, the list of corresponding URIs
	annotatedTexts = getURIsFromText(text, spotlightConfidence, spotlightSupport)

	print(annotatedTexts)
  # Prepare the JSON
  # responseUriArray = []
  # for url, uris in annotatedTexts.items():
	# responseUriArray.append({
		# "url": url,
		# "uri": uris
	  # })

  # response = {
	# "pages": responseUriArray
  # }

  # jsonResponse = json.dumps(response)

	return 0

'''
=========================================================================================
Usage 
python genURI.py Inception 20 all 0.4 34
python genURI.py query searchEngine numberOfResults spotlightConfidence spotlightSupport
=========================================================================================
'''
if	__name__ =='__main__':

  # Default values for spotlightConfidence is 0.2 and for spotlightSupport is 20
	if(1 < len(sys.argv)):
		spotlightConfidence = sys.argv[1]
	else:
		spotlightConfidence = 0.12

	if(2 < len(sys.argv)):
		spotlightSupport = sys.argv[2]
	else:
		spotlightSupport = 20

	jsonResponse = main(spotlightConfidence, spotlightSupport)

	print(jsonResponse)