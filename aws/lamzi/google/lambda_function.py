import json
import re
from random import shuffle

from botocore.vendored import requests


def crawl(search_term='Drake'):
    INFO_REGEX = rb'<h3\s*class="r">\s*<a\s+href="([^"]+)" ping="[^"]+">([^<]+)</a>'
    URL = "https://www.google.ro/search?q={}".format(search_term)

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
    first_results = output[:5]
    other_results = output[5:]
    shuffle(other_results)

    return first_results + other_results


def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        # 'body': json.dumps(event['queryStringParameters'])
        'body': json.dumps(crawl(event['queryStringParameters']['query']))
    }
