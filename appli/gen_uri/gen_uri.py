from gen_uri.bing_search_api import BingSearchAPI
from gen_uri.alchemyapi import AlchemyAPI
from gen_uri.threading_requests import *
from enum import Enum
import xml.etree.ElementTree, sys, re, requests, json, os, getopt

# URLs des APIs
alchemy_root_URL = "http://access.alchemyapi.com/calls"
alchemy_text_search_URL = "/url/URLGetText"
alchemy_concept_search_URL = "/url/URLGetRankedConcepts"
alchemy_get_news = "/data/GetNews"
alchemy_get_concepts_URL = "http://gateway-a.watsonplatform.net/calls/url/URLGetRankedConcepts"
alchemy_get_concepts_text_URL = "http://gateway-a.watsonplatform.net/calls/text/TextGetRankedConcepts"
alchemy_get_entities_URL = "http://gateway-a.watsonplatform.net/calls/url/URLGetRankedNamedEntities"
google_search_URL = "https://www.googleapis.com/customsearch/v1"
bing_search_URL = "https://api.datamarket.azure.com/Bing/Search/Web"
dbpedia_spotlight_URL = "http://spotlight.dbpedia.org/rest/annotate"

# API keys
alchemy_API_key = "9d4bfa22ad347204f33e0451834cef0fe6f5b9e3"
alchemy_API_key_rescue = "cf9f0b681c01368d7329c9c4277c9b7ea91e8732"
alchemy_API_key = "cf9f0b681c01368d7329c9c4277c9b7ea91e8732"
alchemy_API_key_rescue_bis = "1c29f8e0024bf320f7974af9cbe6612ec1dd8d73"
google_API_key = "AIzaSyB23UnDXR2PyYdSygH1ClmUvIHvrdwacDo"
google_API_key_rescue = "AIzaSyA1CXFhP9LGmIFZokfkOjnU78Y32dRYWk0"
search_engine_key = "016723847753961302155:y6-cneh1knc"
search_engine_key_rescue = "001392524783232473057:uwxuk9qp0-a"
bing_search_API_key = "Qf4hLruRDq3/DICqgrhXPVQRlfrebkPCwI0Hd66EgmU"

# fichiers cache utiles durant les tests, pour éviter de spammer les serveurs
directory = 'gen_uri'
google_search_example_file = os.path.join(directory, os.path.join("sample_output", "exampleResponse.json"))
google_searches_example_file = os.path.join(directory, os.path.join("sample_output", "exampleResponses.json"))
bing_search_example_file = os.path.join(directory, os.path.join("sample_output", "bingResponse.json"))
spotlight_example_file = os.path.join(directory, os.path.join("sample_output", "spotlightResponseExample.xml"))
sample_output = os.path.join(directory, os.path.join("sample_output", "gen_uri.json"))

# paramètres globaux de requetes
google_nb_results_per_request = 10
bing_nb_results_per_request = 50
append_keyword_movie = "movie"
enable_writting = False
regex_whitespaces = re.compile(r'\s+')


class SearchType(Enum):
    GOOGLE_ONLY = 1
    BING_ONLY = 2
    GOOGLE_AND_BING = 3


'''
============================================================================
PART 1 : Send a query and retrieve list of URLs
============================================================================
'''
def get_URLs_from_query(query, max_number_of_results=100, search_type=SearchType.GOOGLE_ONLY, append_keyword=False, from_web=False):
    if (max_number_of_results > 100):
        max_number_of_results = 100

    urls = []
    titles = {}

    # If we need to do a real request on the web
    if (from_web):
        if (append_keyword):
            query += " " + append_keyword_movie

        if (search_type == SearchType.GOOGLE_ONLY):
            get_URLs_from_google(query, max_number_of_results, urls, titles)

        elif (search_type == SearchType.BING_ONLY):
            get_URLs_from_bing(query, max_number_of_results, urls, titles)

        elif (search_type == SearchType.GOOGLE_AND_BING):
            # Divide evenly the number of requests between the two search engines
            number_of_requests_per_search_engine = max_number_of_results // 2
            # The remainder will be added to the number of requests of Bing (less restrictive than Google limit wise)
            last_offset_to_add_to_bing = max_number_of_results % 2

            # Google
            get_URLs_from_google(query, number_of_requests_per_search_engine, urls, titles)

            # Bing
            get_URLs_from_bing(query, number_of_requests_per_search_engine + last_offset_to_add_to_bing, urls, titles)

        else:
            # Not a correct search engine, throw error ?
            number_of_requests = max_number_of_results // bing_nb_results_per_request
    else:
        json_content = getSearchFromFile()
        add_google_URL_to_list(urls, titles, json_content)

    return urls, titles


def get_URLs_from_google(query, max_number_of_results, urls, titles):
    if (max_number_of_results < google_nb_results_per_request):

        json_content = get_search_from_google_CSE(query, 1, max_number_of_results, True)
        if not add_google_URL_to_list(urls, titles, json_content):
            json_content = get_search_from_google_CSE(query, 1, max_number_of_results, True)
            add_google_URL_to_list(urls, titles, json_content)
    else:
        # Get the number of requests to do (10 results per request)
        number_of_requests = max_number_of_results // google_nb_results_per_request
        # Get the number of results to return for the last request (remainder of division)
        last_offset = max_number_of_results % google_nb_results_per_request

        for offset in range(0, number_of_requests):
            json_content = get_search_from_google_CSE(query, (offset * google_nb_results_per_request) + 1,
                                                 google_nb_results_per_request, True)
            if not add_google_URL_to_list(urls, json_content):
                json_content = get_search_from_google_CSE(query, (offset * google_nb_results_per_request) + 1,
                                                 google_nb_results_per_request, True)
                add_google_URL_to_list(urls, titles, json_content)

        # If a last request is needed to retrieve the last few results as requested by user
        if (last_offset != 0):
            json_content = get_search_from_google_CSE(query, (offset * google_nb_results_per_request) + last_offset + 1,
                                                 google_nb_results_per_request, True)
            if not add_google_URL_to_list(urls, titles, json_content):
                json_content = get_search_from_google_CSE(query, (offset * google_nb_results_per_request) + last_offset + 1,
                                                 google_nb_results_per_request, True)
                add_google_URL_to_list(urls, titles, json_content)

def get_URLs_from_bing(query, max_number_of_results, urls, titles):
    if (max_number_of_results < bing_nb_results_per_request):
        json_content = get_search_from_bing(query, 0, max_number_of_results, True)
        add_bing_URL_to_list(urls, titles, json_content)
    else:
        # Get the number of requests to do (50 results per request)
        number_of_requests = max_number_of_results // bing_nb_results_per_request
        # Get the number of results to return for the last request (remainder of division)
        last_offset = max_number_of_results % bing_nb_results_per_request

        offset = 0
        for offset in range(0, number_of_requests):
            json_content = get_search_from_bing(query, (offset * bing_nb_results_per_request), bing_nb_results_per_request, True)
            add_bing_URL_to_list(urls, titles, json_content)

        # If a last request is needed to retrieve the last few results as requested by user
        if (last_offset != 0):
            json_content = get_search_from_bing(query, (offset * bing_nb_results_per_request) + last_offset,
                                            bing_nb_results_per_request, True)
            add_bing_URL_to_list(urls, titles, json_content)


def add_google_URL_to_list(urls, titles, json_content):
    json_object = json.loads(json_content)
    if 'items' in json_object:
        for item in json_object['items']:
            link = item['link']
            urls.append(link)
            titles[link] = item['title']
        return True
    else:
        globals()['google_API_key'] = google_API_key_rescue
        globals()['search_engine_key'] = search_engine_key_rescue
        return False


def add_bing_URL_to_list(urls, titles, json_content):
    json_object = json.loads(json_content)

    json_object = json_object['d']

    for result in json_object['results']:
        link = result['Url']
        titles[link] = result['Title']
        urls.append(link)


def getSearchFromFile():
    with open(google_search_example_file, "r") as myfile:
        json_content = myfile.read()

    return json_content


def get_search_from_google_CSE(query, offset=1, number_of_results=google_nb_results_per_request, write_to_file=True):
    payload = {
        "q": query,
        "fields": "items(link,title)",
        "key": google_API_key,
        "cx": search_engine_key,
        "lr": "lang_en",
        "start": offset,
        "num": number_of_results
    }

    response = requests.get(google_search_URL, params=payload)
    json_content = response.text

    if (write_to_file):
        write_content_to_file(google_search_example_file, json_content, True)
        write_content_to_file(google_searches_example_file, json_content, False)

    return json_content


def get_search_from_bing(query, offset=0, number_of_results=bing_nb_results_per_request, write_to_file=True):
    api = BingSearchAPI(bing_search_API_key)
    language = quote('en-US')
    params = {
        "$format": "json",
        "$skip": offset,
        "Market": language,
        "$top": number_of_results
    }

    json_content = api.search_web(query, payload=params)
    
    json_content = json_content.text

    if write_to_file:
        write_content_to_file(bing_search_example_file, json_content)

    return json_content

def quote(query):
    '''Quote query with sign(')'''
    if query.startswith('\'') is not True:
        query = '\'' + query 

    if query.endswith('\'') is not True:
        query = query + '\''         
    
    return query

def write_content_to_file(file_name, content, replace=False):
    if replace:
        flag = "w"
    else:
        flag = "a+"

    with open(file_name, flag) as json_file:
        json_file.write(content)


'''
============================================================================
PART 2 : For each URL, use Alchemy to extract text and semantic data
============================================================================
'''
# Renvoie le texte concatene des 30 premieres plus grandes lignes du texte retourne par alchemy
def get_texts_from_URLs(urls):
    texts = {}
    tab_responses = make_alchemy_request(urls, alchemy_text_search_URL)
    i = 1
    fail = 0
    for url in urls:
        raw_response = tab_responses[i]
        i += 1
        text = ""
        fail = 0
        if  raw_response is not None :
            response = raw_response
            if  response['status'] == 'OK' :
                text = str(response['text'].encode('ascii', errors='ignore'))
                text = clean_text(text, 30)
            else:
                text = ""
                fail+=1
        else:
            fail+=1
        texts[url] = text

    if fail==len(urls):
        globals()['alchemy_API_key'] = alchemy_API_key_rescue
        return get_texts_from_URLs(urls)

    return texts

def make_alchemy_request(urls, alchemy_endpoint = alchemy_text_search_URL):
    params_list = []
    for url in urls:
        param = {}
        param['url'] = url
        param['apikey'] = alchemy_API_key
        param['outputMode'] = 'json'
        param["linkedData"] = "1"
        params_list.append(param)

    p = RequestPool(alchemy_root_URL + alchemy_endpoint, params_list)
    p.launch()
    tab_responses = p.get_results()
    return tab_responses

def clean_text(text, nb_lines_max):
    text = delete_spaces(text)
    lignes = text.split("\\n")
    sorted(lignes, key=lambda x: (len(x)), reverse=True)
    ret = ''
    for i in range(0, min(nb_lines_max, len(lignes))):
        ret += lignes[i]
    return ret


def delete_spaces(text):
    clean_text = ''
    prev = 'a'
    for i in text:
        if ((i == ' ' and prev != ' ') or i != ' '):
            clean_text += i
            prev = i
    return clean_text

def get_concepts_from_alchemy_BIS(urls):
    concepts = []
    responses = make_alchemy_request(urls,alchemy_concept_cearch_URL)
    i=1
    for url in urls :
        response = responses[i]
        i+=1
        dbpedia_concepts = []
        if response is not None :
            if response['status'] == 'OK':
                response_concepts = response['concepts']
                for concept in response_concepts :
                    if 'dbpedia' in concept:
                        dbpedia_concepts.append(concept['dbpedia'])

        concepts.append({'url':url,'concepts':dbpedia_concepts})
    return concepts

def get_concepts_from_alchemy_by_texts(texts):
    uris = {}
    for url, text in texts.items:
        uris[url] = get_concepts_from_alchemy_by_text(text)

    return uris


def get_concepts_from_alchemy_by_text(text):
    payload = {
        "text": url,
        "apikey": alchemy_API_key,
        "outputMode": "json",
        "linkedData": "1"
    }

    response = requests.get(alchemy_get_concepts_URL, params=payload)
    
    json_content = response.text

    json_object = json.loads(json_content)

    uris = []
    for uri in json_object['concepts']:
        if 'dbpedia' in uri:
            uris.append(uri['dbpedia'])

    return uris

def get_entities_from_alchemy_by_urls(urls):
    uris = {}
    for url in urls:
        uris[url] = get_entities_from_alchemy_by_url(url)

    return uris


def get_entities_from_alchemy_by_url(url):
    payload = {
        "url": url,
        "apikey": alchemy_API_key,
        "outputMode": "json",
        "linkedData": "1"
    }

    response = requests.get(alchemy_get_entities_URL, params=payload)

    json_content = response.text

    json_object = json.loads(json_content)

    uris = []
    for uri in json_object['entities']:
        if 'disambiguated' in uri:
            entity = uri['disambiguated']
            if 'dbpedia' in entity:
                uris.append(entity['dbpedia'])

    return uris


'''
============================================================================
PART 3 : For each Alchemy text output, use Spotlight to find related URI
============================================================================
'''
def make_spotlight_requests(texts, spotlight_confidence, spotlight_support) :
    spot_params = []
    for url, text in texts.items():
        if text and not text.isspace():
            spotParam = prepare_spotlight_request(text, spotlight_confidence, spotlight_support)
            spot_params.append(spotParam)

    p = RequestPool(dbpedia_spotlight_URL, spot_params)
    p.launch()
    return p.get_results()


def prepare_spotlight_request(text, spotlight_confidence, spotlight_support):
    payload = {
        "text": text,
        "confidence": spotlight_confidence,
        "support": spotlight_support
        # "sparql": sparql
    }
    return payload;


def get_concepts_from_alchemy(url):
    payload = {
        "url": url,
        "apikey": alchemy_API_key,
        "outputMode": "json",
        "linkedData": "1"
    }

    response = requests.get(alchemy_get_concepts_URL, params=payload)
    
    json_content = response.text

    json_object = json.loads(json_content)

    uris = []
    for uri in json_object['concepts']:
        if 'dbpedia' in uri:
            uris.append(uri['dbpedia'])

    return uris


def get_URIs_from_texts(texts, spotlight_confidence, spotlight_support):
    annotated_texts = {}
    for url, text in texts.items():
        if text and not text.isspace():
            uris = get_URIs_from_text(text, spotlight_confidence, spotlight_support)
            urisFromAlchemyConcepts = get_concepts_from_alchemy(url)
            urisFromAlchemyEntities = get_entities_from_alchemy_by_url(url)
            uris = uris + urisFromAlchemyConcepts + urisFromAlchemyEntities
            annotated_texts[url] = uris

    return annotated_texts


def get_URIs_from_text(text, spotlight_confidence, spotlight_support):
    content = get_annotated_text_from_spotlight(text, spotlight_confidence, spotlight_support, None)
    # content = get_annotated_text_from_file()

    # Extract URI
    uris = get_DBPedia_ressources(content)

    return uris


def get_annotated_text_from_file():
    with open(spotlight_example_file, "r") as myfile:
        content = myfile.read()

    return content


def get_annotated_text_from_spotlight(text, spotlight_confidence, spotlight_support, write_to_file):
    payload = {
        "text": text,
        "confidence": spotlight_confidence,
        "support": spotlight_support
        # "sparql": sparql
    }
    response = requests.post(dbpedia_spotlight_URL, data=payload)

    content = response.text

    if write_to_file:
        write_content_to_file(spotlight_example_file, content)

    return content


def get_DBPedia_ressources(xml_raw_content):
    if not xml_raw_content:
        return []
    with open('test', 'w+') as f:
        f.write(xml_raw_content)
    xmlRoot = xml.etree.ElementTree.fromstring(xml_raw_content)
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
@max_number_of_results : The number of results to return (integer) (max 100)
@search_type : The type of search (SearchType enum)
@spotlight_confidence : The confidence for Spotlight
@spotlight_support : The support for Spotlight
@from_web : if the search is done on the web or from a saved version of the request
============================================================================
'''
def main(query, max_number_of_results, search_type, spotlight_confidence, spotlight_support, from_web, append_keyword):
    # Retrieve URLS based on query
    (urls, titles) = get_URLs_from_query(query, max_number_of_results, search_type, append_keyword, from_web)

    # Retrieve, for each URL, an associated text
    texts = get_texts_from_URLs(urls)
  
    # Retrieve, for each text, the list of corresponding URIs
    annotated_texts = get_URIs_from_texts(texts, spotlight_confidence, spotlight_support)

    # Prepare the JSON
    response_URI_array = []
    for url, uris in annotated_texts.items():
        title = titles[url]
        response_URI_array.append({
            "url": url,
            "title": title,
            "uri": uris
        })

    response = {
        "pages": response_URI_array
    }

    json_response = json.dumps(response)

    write_content_to_file(sample_output, json_response)
    return json_response


'''
=========================================================================================================
Usage 
python genURI.py Inception 20 all 0.4 34 True
python genURI.py query number_of_results searchEngine spotlight_confidence spotlight_support append_keyword
=========================================================================================================
'''
if __name__ == '__main__':
    query = sys.argv[1]

    # Number of results to return from queries
    if (2 < len(sys.argv)):
        max_number_of_results = int(sys.argv[2])
    else:
        max_number_of_results = 20

    # Search engine on which to search results for
    if (3 < len(sys.argv)):
        if (sys.argv[3] == "google"):
            search_type = SearchType.GOOGLE_ONLY
        elif (sys.argv[3] == "bing"):
            search_type = SearchType.BING_ONLY
        elif (sys.argv[3] == "all"):
            search_type = SearchType.GOOGLE_AND_BING
        else:
            search_type = SearchType.GOOGLE_ONLY
    else:
        search_type = SearchType.GOOGLE_ONLY

    # Default values for spotlight_confidence is 0.2 and for spotlight_support is 20
    if (4 < len(sys.argv)):
        spotlight_confidence = sys.argv[4]
    else:
        spotlight_confidence = 0.2

    if (5 < len(sys.argv)):
        spotlight_support = sys.argv[5]
    else:
        spotlight_support = 20

    if (6 < len(sys.argv)):
        append_keyword = sys.argv[6]
    else:
        append_keyword = False

    json_response = main(query, max_number_of_results, search_type, spotlight_confidence, spotlight_support, append_keyword)

    print(json_response)
