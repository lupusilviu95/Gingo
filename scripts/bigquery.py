from google.cloud import bigquery

def create_dataset(dataset_id):
    bigquery_client = bigquery.Client()

    dataset_ref = bigquery_client.dataset(dataset_id)
    dataset = bigquery.Dataset(dataset_ref)

    dataset = bigquery_client.create_dataset(dataset)

    print('Dataset {} created'.format(dataset.dataset_id))
