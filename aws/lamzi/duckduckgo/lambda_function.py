import json
from botocore.vendored import requests
import urllib.parse
import re

def crawl(search_term='Drake'):

    INFO_REGEX = rb'class="result__a" href="[^;]+;uddg=([^"]+)"'
    URL = "https://duckduckgo.com/html/?q={}".format(search_term)
    
    response = requests.get(URL)
    response_content = response.content
    results = re.findall(INFO_REGEX, response_content, flags=re.DOTALL)
    links = results if results else []
    links = [urllib.parse.unquote(link.decode("utf-8")) for link in links]
    return {"a": str(response.content)}

def _crawl(search_term='Drake'):

    INFO_REGEX = rb'<h3\s*class="r">\s*<a\s+href="([^"]+)" ping="[^"]+">([^<]+)</a>'
    QUERY_STRING = "weather+dublin"
    URL = "https://www.google.ro/search?q={}?start=10".format(QUERY_STRING)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    }
    
    response = requests.get(URL, headers=headers)
    response_content = response.content
    output = []
    results = re.findall(INFO_REGEX, response_content)
    if results:
        for result in results:
            output.append({
                "url": result[0].decode("utf-8"),
                "snippet": result[1].decode("utf-8"),
            })
    return output



def lambda_handler(event, context):
    
    return {
        'statusCode': 200,
        'headers': { 'Content-Type': 'application/json' },
        # 'body': json.dumps(event['queryStringParameters'])
        'body': json.dumps( _crawl(event['queryStringParameters']['query']) )
    }

    
