import logging
import requests
import json

from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap
from scripts import bigquery
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

BASE_URL = "https://85j17hnivk.execute-api.eu-west-1.amazonaws.com/prod"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
}

MAX_RESULTS = 10
SCORES = {"google": 0.45, "bing": 0.35, "duckduckgo": 0.20}

app = Flask(
    __name__,
    template_folder='client/views',
    static_folder='client/static'
)
Bootstrap(app)


def get_results(url, params):
    response = requests.get(url.geturl(), headers=HEADERS, params=params)
    response = json.loads(response.content.decode("utf-8"))
    return response if type(response) is list else []

def get_domain_for_url(url):
    parsed_uri = urlparse(url)
    return '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)

def aws_search(query):
    cached_results = bigquery.search(query)

    if len(cached_results) == 0:
        google_url = urlparse(BASE_URL + "/google")
        bing_url = urlparse(BASE_URL + "/bing")
        duck_url = urlparse(BASE_URL + "/duckduckgo")
        params = {"query": query}

        results_by_engine = {}
        future_to_engine_result = {}
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_engine_result[executor.submit(get_results, google_url, params)] = "google"
            future_to_engine_result[executor.submit(get_results, bing_url, params)] = "bing"
            future_to_engine_result[executor.submit(get_results, duck_url, params)] = "duckduckgo"

            for future in as_completed(future_to_engine_result):
                engine = future_to_engine_result[future]
                try:
                    results_by_engine[engine] = future.result()
                except Exception as err:
                    print("Exception generated by:{}. Error {}".format(engine, err))
                    results_by_engine[engine] = []

        links = {}

        for engine, results in results_by_engine.items():
            for index, result in enumerate(results):
                already_found = links.get(result["url"], {})
                already_found[engine] = index
                already_found["snippet"] = result["snippet"] if len(result["snippet"]) > len(
                    already_found.get("snippet", "")) else already_found.get("snippet", "")
                links[result["url"]] = already_found

        for link, engine_results in links.items():
            score = 0
            for engine, position in engine_results.items():
                if engine != "snippet":
                    score += SCORES[engine] * (MAX_RESULTS - position)
            links[link]["score"] = '%.2f' % score
            links[link]["domain"] = get_domain_for_url(link)

        err = bigquery.insert(query, sorted(links.items(), key=lambda a: a[1]["score"], reverse=True))
        return sorted(links.items(), key=lambda a: a[1]["score"], reverse=True)

    return json.loads(cached_results[0])


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', title='Gingo Search')
    elif request.method == 'POST':
        query = request.form['query']
        results = aws_search(query)
        return render_template('index.html', title='Gingo Search', results=results)
    else:
        return "Unknown method"


@app.route('/search')
def search():
    query = request.args.get("query")
    results = aws_search(query)
    err = bigquery.insert(query, results)
    return jsonify(results)


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
