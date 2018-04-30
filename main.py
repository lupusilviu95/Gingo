# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
import logging
import requests 
import json

from flask import Flask, request
from flask.json import jsonify

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from scripts import bigquery

BASE_URL = "https://rbelb0crz5.execute-api.eu-central-1.amazonaws.com/prod"
HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    }

MAX_RESULTS = 10
SCORES = {"google": 0.45, "bing": 0.35, "duckduckgo": 0.20}

app = Flask(__name__)


@app.route('/search')
def search():
    query = request.args.get("query")
    google_url = urlparse(BASE_URL + "/google")
    bing_url = urlparse(BASE_URL + "/bing")
    duck_url = urlparse(BASE_URL + "/duckduckgo")
    params = {"query": query}
    google_response = requests.get(google_url.geturl(), headers=HEADERS, params=params)
    bing_response = requests.get(bing_url.geturl(), headers=HEADERS, params=params)
    duck_response = requests.get(duck_url.geturl(), headers=HEADERS, params=params)

    google_results = json.loads(google_response.content)
    bing_results = json.loads(bing_response.content)
    duckduckgo_results = json.loads(duck_response.content)

    results_by_engine = {"google": google_results, "bing": bing_results, "duckduckgo": duckduckgo_results}

    links = {}

    for engine, results in results_by_engine.items():
        for index, result in enumerate(results):
            already_found = links.get(result["url"], {})
            already_found[engine] = index
            already_found["snippet"] = result["snippet"] if len(result["snippet"]) > len(already_found.get("snippet", "")) else already_found.get("snippet", "")
            links[result["url"]] = already_found
    

    for link, engine_results in links.items():
        score = 0 
        for engine, position in engine_results.items():
            if engine != "snippet":
                score += SCORES[engine] * (MAX_RESULTS - position)
        links[link]["score"] = score


    return jsonify(sorted(links.items(), key=lambda a: a[1]["score"], reverse=True))


@app.route('/test/<string:test_param>')
def test(test_param):
    """ Testing """
    bigquery.create_dataset(test_param)

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END app]
