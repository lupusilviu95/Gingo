import logging
import requests 
import json


from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap
from scripts import bigquery

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

BASE_URL = "https://rbelb0crz5.execute-api.eu-central-1.amazonaws.com/prod"
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

def aws_search(query):
    cached_results = bigquery.search(query)

    if len(cached_results) == 0:
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

        err = bigquery.insert(query, sorted(links.items(), key=lambda a: a[1]["score"], reverse=True))
        return sorted(links.items(), key=lambda a: a[1]["score"], reverse=True)
    else:
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
