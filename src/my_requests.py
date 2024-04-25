import clr, sys, os, System
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'json.zip'))
import json


clr.AddReference('System')
from System import Uri

clr.AddReference('System.Net.Http')
from System.Net.Http import HttpClient, HttpMethod, HttpContent, StringContent

clr.AddReference('System.Net')
from System.Net import HttpWebRequest, Cookie, DecompressionMethods, WebUtility


def post(url, json_data):
    # Create HttpClient instance
    client = HttpClient()

    # Serialize JSON data
    json_content = json.dumps(json_data, ensure_ascii=False)
    # Create StringContent with JSON data
    content = StringContent(json_content)
    # Set content type header
    content.Headers.ContentType = System.Net.Http.Headers.MediaTypeHeaderValue("application/json")

    # Send POST request
    response = client.PostAsync(url, content).Result

    # Check if request was successful
    if response.IsSuccessStatusCode:
        # Read response content
        response_content = response.Content.ReadAsStringAsync().Result
        # Deserialize JSON content
        json_object = json.loads(response_content)
        return json_object
    else:
        # Print error message if request failed
        print("Error:", response.StatusCode, response.ReasonPhrase)
        return None

  
""" 
def post(url, data):
    try:
        System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12
        req = HttpWebRequest.Create(Uri(url))
        req.Method = "POST"
        req.ContentType = "application/json"

        json_data = json.dumps(bytes(data))

        reqStream = req.GetRequestStream()
        streamWriter = System.IO.StreamWriter(reqStream)
        streamWriter.Write(json_data)
        streamWriter.Flush()
        streamWriter.Close()

        res = req.GetResponse()
        if res.StatusCode == System.Net.HttpStatusCode.OK:
            responseStream = res.GetResponseStream()
            reader = System.IO.StreamReader(responseStream)
            responseData = reader.ReadToEnd()
            return responseData
    except Exception as e:
        print(e)
        return None
"""


def get(url):
    # Create HttpClient instance
    client = HttpClient()

    # Send GET request
    response = client.GetAsync(url).Result

    # Check if request was successful
    if response.IsSuccessStatusCode:
        # Read response content
        response_content = response.Content.ReadAsStringAsync().Result
        # Deserialize JSON content
        json_object = json.loads(response_content)
        return json_object
    else:
        # Print error message if request failed
        print("Error:", response.StatusCode, response.ReasonPhrase)
        return None


def _read_url(url):
  
    page = ''
    requestUri = quote(url)
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


def quote(url, safe="%/:=&~#+$!,?;'@()*[]\""):
    encodedURL = WebUtility.UrlEncode(url)
    
    for safeChar in safe:
        encodedURL = encodedURL.Replace(Uri.HexEscape(safeChar), safeChar.ToString())
        
    return encodedURL
