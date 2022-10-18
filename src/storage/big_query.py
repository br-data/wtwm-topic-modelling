from settings import BIGQUERY_PROJECT_ID, BIGQUERY_DATASET_ID, BIGQUERY_CREDENTIAL_PATH
from google.oauth2 import service_account
from google.cloud.bigquery import LoadJobConfig, SourceFormat, Client


class BigQueryWriter:
    def __init__(self) -> None:
        self.project_id = BIGQUERY_PROJECT_ID
        self.dataset_id = BIGQUERY_DATASET_ID
        self.credentials = service_account.Credentials.from_service_account_file(
            BIGQUERY_CREDENTIAL_PATH
        )
        self.client = Client(credentials=self.credentials, project=self.project_id)

    def write_file(self, file_path: str, table_id: str):
        """Write comments into the BigQuery table specified by table_id.

        :param file_path: path to file to load to database
        :param table_id: id of the table to write into
        """
        # create a dataset reference
        dataset_ref = self.client.dataset(self.dataset_id)

        # create a table reference
        table_ref = dataset_ref.table(table_id)

        # create a load job config
        load_job_config = LoadJobConfig()
        load_job_config.source_format = SourceFormat.NEWLINE_DELIMITED_JSON
        load_job_config.autodetect = True

        # load the data
        job = self.client.load_table_from_file(
            open(file_path, "rb"), table_ref, job_config=load_job_config
        )
        job.result()
