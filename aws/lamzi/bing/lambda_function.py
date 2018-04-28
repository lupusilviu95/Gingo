import json
from botocore.vendored import requests

def crawl(search_term='Drake'):
    subscription_key = "1885326d206f4d50a3cc0b5e33894e0c"
    search_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"
    
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {"q": search_term, "textDecorations": True, "textFormat": "HTML"}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    
    values = search_results["webPages"]["value"]
    links = []
    for v in values:
        links.append({"url" : v["url"], "snippet" : v["snippet"]})
    
    return links


def lambda_handler(event, context):
    
    return {
        'statusCode': 200,
        'headers': { 'Content-Type': 'application/json' },
        'body': json.dumps( crawl(event['queryStringParameters']['query']) )
    }

    
