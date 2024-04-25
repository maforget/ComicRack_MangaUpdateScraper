import clr, re, my_requests

clr.AddReference('System')
import System

clr.AddReference('System.Net')
from System.Net import WebUtility

from System.Collections.Generic import *


DEBUG_LEVEL = 1 #0 - Disable DEBUG #1 = fields only, #2 = Include raw json
GET_INFO_FROM_SERIES_PAGE = False # Prevents unnecessary API calls to the serie if not in use, just fetches Writer & Penciller.
separator = "=" * 30
long_separator = "-" * 60

#@Name MangaUpdates Scraper
#@Hook Books, Editor
#@Enabled false
#@Image manga-updates.png
#@Description Scraps MangaUpdates (API)
def MangaUpdateScraper(books):
    if DEBUG_LEVEL >= 1: print(separator + " Start " + separator)

    pSeries = ""
    pURL = ""
    pGenre = ""
    pDescription = ""
    pID = 0
    pAuthor = ""
    pArtist = ""

    for book in books:
        if DEBUG_LEVEL >= 1: print("Processing book: " + book.Series)
        cURL = ""
        cGenre = ""
        cDescription = ""
        cID = 0
        cAuthor = ""
        cArtist = ""

        #Same Series, use previous info
        if pSeries and pSeries == book.Series:
            cURL = pURL
            cGenre = pGenre
            cID = pID
            cDescription = pDescription
            cAuthor = pAuthor
            cArtist = pArtist

        else:
            json_data = MangaUpdateAPISearch(book.Series)
            data = []
            if json_data and len(json_data['results']) > 0:
                data = [item for item in json_data['results'] if item.get('hit_title') == book.Series]
                #returns the 1st one, if the book.Series isn't found in the page.
                data = data[0] if data and len(data) > 0 else json_data['results'][0] # TODO: add a form for selection
            if data:
                pSeries = book.Series # Set pSeries for next album
                record = data['record']
         
                name = WebUtility.HtmlDecode(data['hit_title'])
                cID = pID = record['series_id']
                cURL = pURL = record['url']
                cGenre = pGenre = WebUtility.HtmlDecode(toString(record['genres'], 'genre'))
                cDescription = pDescription = strip_tags(WebUtility.HtmlDecode(record['description']))

                # For Debug
                serie = book.Series if name == book.Series else name
                if DEBUG_LEVEL >= 1: print("--> id: " + str(cID))
                if DEBUG_LEVEL >= 1: print("--> series: " + serie)
                if DEBUG_LEVEL >= 1: print("--> url: " + cURL)
                if DEBUG_LEVEL >= 1: print("--> genre: " + cGenre)
                if DEBUG_LEVEL >= 1: print("--> description: " + cDescription)

                if GET_INFO_FROM_SERIES_PAGE:
                    series_info = MangaUpdateAPISeries(cID)
                    if series_info and len(series_info) > 0:
                        cAuthors_data = [item for item in series_info['authors'] if item.get('type') == "Author"]
                        cAuthor = pAuthor = WebUtility.HtmlDecode(toString(cAuthors_data, 'name'))
                        if DEBUG_LEVEL >= 1: print("--> Author: " + cAuthor)

                        cArtist_data = [item for item in series_info['authors'] if item.get('type') == "Artist"]
                        cArtist = pArtist = WebUtility.HtmlDecode(toString(cArtist_data, 'name'))
                        if DEBUG_LEVEL >= 1: print("--> Artist: " + cArtist)


        if cGenre:
            book.Genre = cGenre

        
        # Remove the # in front of the desired fields you want to save to ComicRack

        # if cID:
        #     book.SetCustomValue('mangaupdates_seriesid', str(cID))

        # if cDescription:
        #     book.Summary = cDescription

        # if cURL:
        #     book.Web = cURL
        
        # Also make sure to set GET_INFO_FROM_SERIES_PAGE = True if you want the following to be saved
        
        # if cAuthor:
        #     book.Writer = cAuthor

        # if cArtist:
        #     book.Penciller = cArtist

        if DEBUG_LEVEL >= 1: print(separator + " END " + separator)



"""
Searches the API for the series provided, returns a json
"""
def MangaUpdateAPISearch(series):
    baseApiURL = "https://api.mangaupdates.com/v1"
    searchApiURL = baseApiURL + "/series/search"
    search_params = {
        "search": series,
        "page": 1,
        "perpage": 5,
        "stype": "title",
        "filter_types": [
            "Novel"
        ]
    }
    
    try:
        response = my_requests.post(searchApiURL, search_params)
        if response:
            if DEBUG_LEVEL >= 2: print(long_separator)
            if DEBUG_LEVEL >= 2: print(response)
            if DEBUG_LEVEL >= 2: print(long_separator)
            return response
        else:
            return None
    except Exception as e:
        print(e)
        return None


"""
Takes the series_id (int) and returns the json using the API
"""
def MangaUpdateAPISeries(id):
    baseApiURL = "https://api.mangaupdates.com/v1"
    seriesApiURL = baseApiURL + "/series/" + str(id)
    
    try:
        response = my_requests.get(seriesApiURL)
        if response:
            if DEBUG_LEVEL >= 2: print(long_separator)
            if DEBUG_LEVEL >= 2: print(response)
            if DEBUG_LEVEL >= 2: print(long_separator)
            return response
        else:
            return None
    except Exception as e:
        # print(e)
        return None


"""
Takes an json array and a key and return it as a string comma separated
"""
def toString(array, key):
    values = [item[key] for item in array]
    return ', '.join(values)


"""
Removes html tags from text.
"""
def strip_tags(html):
    try:
        return re.sub("<[^<>]+?>", "", html, re.IGNORECASE | re.DOTALL | re.MULTILINE)
    except:
        return html
