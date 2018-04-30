import json

from datetime import datetime
from google.cloud import bigquery


def insert(query, data):
	bigquery_client = bigquery.Client.from_service_account_json(
        '/home/lupus/Faculty/Gingo/scripts/service_account.json')
	dataset_ref = bigquery_client.dataset("search")
	table_ref = dataset_ref.table("result")
	table = bigquery_client.get_table(table_ref)
	rows_to_insert = [(query, json.dumps(data), str(datetime.now()))]
	errors = bigquery_client.insert_rows(table, rows_to_insert)
	return errors

def search(query):
	bigquery_client = bigquery.Client.from_service_account_json(
        '/home/lupus/Faculty/Gingo/scripts/service_account.json')

	query_job = bigquery_client.query("Select * from `pcd-hw3-gingo.search.result` where query=\"{}\";".format(query))
	results = []
	for result in query_job.result():
		results.append((result.get("links")))
	return results

