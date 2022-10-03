'''class to load prodigy data into google BigQuery'''

from google.cloud import bigquery
from google.oauth2 import service_account
from google.cloud.bigquery import LoadJobConfig
from google.cloud.bigquery import SourceFormat
from os import path

class LoadData:
    def __init__(self):
        self.credentials = service_account.Credentials.from_service_account_file(
            '.credentials/journalismai-credentials.json')
        self.project_id = 'journalismai-362410'
        self.dataset_id = 'wtwm'
        self.client = bigquery.Client(credentials=self.credentials, project=self.project_id)

    def load_data(self, file_name: str, table_id: str):
        '''loads comments data into the BigQuery table specified by table_id'''

        # create a dataset reference
        dataset_ref = self.client.dataset(self.dataset_id)

        # create a table reference
        table_ref = dataset_ref.table(table_id)

        # create a load job config
        load_job_config = LoadJobConfig()
        load_job_config.source_format = SourceFormat.NEWLINE_DELIMITED_JSON
        load_job_config.autodetect = True

        # load the data
        with open(path.abspath('.') + '/data/' + file_name, 'rb') as source_file:
            job = self.client.load_table_from_file(source_file, table_ref, job_config=load_job_config)
            job.result()
