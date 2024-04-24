import clr, re, System

clr.AddReference('System')
clr.AddReference('System.Net')

from System import Uri
from System.Net import HttpWebRequest, Cookie, DecompressionMethods, WebUtility
from System.Collections.Generic import *

from collections import OrderedDict

#@Name MangaUpdates Scraper
#@Hook Books, Editor
#@Enabled false
#@Image manga-updates.png
#@Description Scraps MangaUpdates
def MangaUpdateScraper(books):
    pSeries = ""
    pURL = ""
    pGenre = ""

    for book in books:
        cURL = ""
        cGenre = ""

        #Same Series, use previous url
        if pSeries and pSeries == book.Series:
            cURL = pURL
            cGenre = pGenre
        else:
            d = MangaUpdateSearch(book.Series)# returns a dict with a tuple for value. First value is url, second is genre
            tuple = ()
            if len(d) > 0:
                # TODO: add a form for selection, returns the 1st one, if the book.Series isn't found in the page.
                tuple = d.get(book.Series, d.values()[0]) 
            if tuple:
                pSeries = book.Series # Set pSeries for next album
                cURL = pURL = tuple[0]
                cGenre = pGenre = tuple[1]

                # For Debug
                serie = book.Series if book.Series in d else d.keys()[0]
                print("==> series: " + serie)
                print("    url: " + cURL)
                print("    genre: " + cGenre)

        if cGenre:
            book.Genre = cGenre

        # if cURL:
        #     book.Web = cURL


def MangaUpdateSearch(text):
    d = OrderedDict()
    baseURL = "https://www.mangaupdates.com"
    searchURL = baseURL + "/search.html?search=" + text
    text = _read_url(searchURL)
    if text:
        for regex in re.finditer(r"""<div class="[^<>]+"><a href='(?P<url>[^<>]+/series/[^<>]+)'\s+alt='Series Info'.*?>(?P<name>[^<>]+)</.+?title="(?P<genre>[^<>]+)">""", text, re.IGNORECASE | re.DOTALL):
            url = regex.group("url").strip()
            name = WebUtility.HtmlDecode(regex.group("name")).strip()
            genre = WebUtility.HtmlDecode(regex.group("genre")).strip()

            # For Debug
            # print("==> name: " + name)
            # print("    url: " + url)
            # print("    genre: " + genre)

            if name and not name.lower().endswith("(novel)"):
                d[name] = (url, genre)
    return d


def _read_url(url):
  
    page = ''
    requestUri = quote(url, safe = "%/:=&~#+$!,?;'@()*[]\"")
    print("Reading URL: " + requestUri)

    try:
        System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12
        Req = System.Net.HttpWebRequest.Create(requestUri)
        #Req.CookieContainer = CookieContainer
        Req.Timeout = 15000
        Req.UserAgent = 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; WOW64; Trident/6.0)'
        Req.AutomaticDecompression = DecompressionMethods.Deflate | DecompressionMethods.GZip
        Req.Headers.Add('X-Powered-By', 'PHP/5.3.17')
        Req.Referer = requestUri
        Req.Accept = 'text/html, application/xhtml+xml, */*'
        Req.Headers.Add('Accept-Language','en-GB,it-IT;q=0.8,it;q=0.6,en-US;q=0.4,en;q=0.2')
        Req.KeepAlive = True
        webresponse = Req.GetResponse()
        a = webresponse.Cookies

        # Application.DoEvents()

        inStream = webresponse.GetResponseStream()        
        encode = System.Text.Encoding.GetEncoding("utf-8")
        ReadStream = System.IO.StreamReader(inStream, encode)   
        page = ReadStream.ReadToEnd()
            
    except Exception as e:
        print(e)
    
    inStream.Close()
    webresponse.Close()
    
    # print(page)
    return page


def quote(url, safe=''):
    # encodedURL = Uri.EscapeUriString(url)
    encodedURL = WebUtility.UrlEncode(url)
    
    for safeChar in safe:
        encodedURL = encodedURL.Replace(Uri.HexEscape(safeChar), safeChar.ToString())
        
    return encodedURL