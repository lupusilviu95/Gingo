from __future__ import print_function
import requests
import json

SEARCH_TERMS = "Drake,Cloud Computing,UEFA Champions League,cozonac,CAP theorem,Life of Pi,1 Mai,BMW,Iasi,USA".split(",")


latency_results = {}
for search_term in SEARCH_TERMS:
    latency_results[search_term] = []
    for i in range(10):
        response = requests.post("https://pcd-hw3-gingo.appspot.com/", data={"query": search_term})
        latency_results[search_term].append(response.elapsed.total_seconds())


with open("results.json", "w") as out_file:
    json.dump(latency_results, out_file)

