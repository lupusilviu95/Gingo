import logging
import requests 
import json

from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap



AWS_LAMBDA_BING = "https://rbelb0crz5.execute-api.eu-central-1.amazonaws.com/prod/bing?query={}"
AWS_LAMBDA_GOOGLE= "https://rbelb0crz5.execute-api.eu-central-1.amazonaws.com/prod/google?query={}"
AWS_LAMBDA_DUCKDUCKGO = "https://rbelb0crz5.execute-api.eu-central-1.amazonaws.com/prod/duckduckgo?query={}"


app = Flask(
    __name__,
    template_folder='client/views',
    static_folder='client/static'
    )

Bootstrap(app)


@app.route('/', methods=['GET'])
def index():
    # """Return a friendly HTTP greeting."""
    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36",
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    # }

    # response = requests.get("https://rbelb0crz5.execute-api.eu-central-1.amazonaws.com/prod/google?query=zacusca", headers=headers)
    # return response.content
    return render_template('index.html', title='Gingo')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('search.html')
    elif request.method == 'POST':
        query = request.form['query']

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        }

        request_url_google = AWS_LAMBDA_GOOGLE.format(query)
        response_google = requests.get(request_url_google, headers=headers)
        response_google = json.loads(response_google.content)

        return render_template('search.html', results=response_google)

        # request_url_bing = AWS_LAMBDA_BING.format(query)
        # response_bing = requests.get(request_url_bing, headers=headers)

        # request_url_duckduckgo = AWS_LAMBDA_DUCKDUCKGO.format(query)
        # response_duckduckgo = requests.get(request_url_duckduckgo, headers=headers)
        # return render_template()
    else:
        return 'Unknown method'


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
