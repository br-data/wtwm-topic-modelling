from settings import BIGQUERY_PROJECT_ID, BIGQUERY_DATASET_ID, BIGQUERY_CREDENTIAL_PATH
from google.oauth2 import service_account
from google.cloud.bigquery import LoadJobConfig, SourceFormat, Client, Table
from random import randint
from datetime import datetime
from pytz import utc



class BigQueryWriter:
    def __init__(self) -> None:
        self.project_id = BIGQUERY_PROJECT_ID
        self.dataset_id = BIGQUERY_DATASET_ID
        self.credentials = service_account.Credentials.from_service_account_file(
            BIGQUERY_CREDENTIAL_PATH
        )
        self.client = Client(credentials=self.credentials, project=self.project_id)
    
    def get_schema_path(self, table_id: str):
        schema_path = table_id.replace(self.project + '.', '').replace('.', '/', 1)
        return 'schemas/' + schema_path + '.json'
    
    def create_table(self, table_id: str, schema=None, expiracy_hours: int = None):
        """Create a temporary table with a random id.

        :param table_id: id of the table to write into
        :param schema: schema of the table
        :param expiracy_hours: number of hours before the table expires
        """
        
        if expiracy_hours is not None:
            suffix = randint(10000, 99999)
            table_id += '_temp_' + str(suffix)
            expiracy_date = datetime.now(utc) + datetime.timedelta(hours=expiracy_hours)

        table = Table(table_id, schema=schema)
        if expiracy_hours is not None:
            table.expires = expiracy_date
        table = self.client.create_table(table)
        if expiracy_hours is not None:
            return table_id

    def write_file(self, file_path: str, table_id: str):
        """Write comments into the BigQuery table specified by table_id.

        :param file_path: path to file to load to database
        :param table_id: id of the table to write into
        """
        # create a dataset reference
        dataset_ref = self.client.dataset(self.dataset_id)

        # create destiny table reference
        table_ref = dataset_ref.table(table_id)

        # create temporary table
        schema_path = self.get_schema_path(table_id)
        schema = self.client.schema_from_json(schema_path)
        temp_table_id = self.create_table(table_id, schema)
        temp_table_ref = dataset_ref.table(temp_table_id)

        # create a load job config
        load_job_config = LoadJobConfig()
        load_job_config.source_format = SourceFormat.NEWLINE_DELIMITED_JSON
        load_job_config.autodetect = True

        # load the data
        job = self.client.load_table_from_file(
            open(file_path, "rb"), temp_table_ref, job_config=load_job_config
        )
        job.result()
