import json
import re
import urllib.parse

import requests

HEADERS = {
}


def crawl(search_term='Drake'):
    INFO_REGEX = rb'class="result__a" href="[^;]+;uddg=([^"]+)"'
    URL = "https://duckduckgo.com/html/?q={}".format(search_term)

    response = requests.get(URL, headers=HEADERS)
    response_content = response.content
    results = re.findall(INFO_REGEX, response_content, flags=re.DOTALL)
    links = results if results else []
    links = [urllib.parse.unquote(link.decode("utf-8")) for link in links]
    links = [{"url": link} for link in links]
    return links


def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        "body": json.dumps(event["queryStringParameters"]),
        # 'body': json.dumps(crawl(event['queryStringParameters']['query']))
    }


if __name__ == '__main__':
    print(crawl("Drake"))
