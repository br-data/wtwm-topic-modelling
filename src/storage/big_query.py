from settings import BIGQUERY_PROJECT_ID, BIGQUERY_DATASET_ID, BIGQUERY_CREDENTIAL_PATH, TABLE_ID
from google.oauth2 import service_account
from google.cloud.bigquery import LoadJobConfig, SourceFormat, Client, Table
from random import randint
from datetime import datetime, timedelta
from pytz import utc

from src.models import Comment


class BigQueryWriter:
    def __init__(self) -> None:
        self.project_id = BIGQUERY_PROJECT_ID
        self.dataset_id = BIGQUERY_DATASET_ID
        self.credentials = service_account.Credentials.from_service_account_file(
            BIGQUERY_CREDENTIAL_PATH
        )
        self.client = Client(credentials=self.credentials, project=self.project_id)

    def create_table(self, table_id: str, schema=None, expiracy_hours: int = None):
        """Create a temporary table with a random id.

        :param table_id: id of the table to write into
        :param schema: schema of the table
        :param expiracy_hours: number of hours before the table expires
        """

        if expiracy_hours is not None:
            suffix = randint(10000, 99999)
            table_id += '_temp_' + str(suffix)
            expiracy_date = datetime.now(utc) + timedelta(hours=expiracy_hours)

        table = Table(table_id, schema=schema)
        if expiracy_hours is not None:
            table.expires = expiracy_date

        self.client.create_table(table)
        if expiracy_hours is not None:
            return table_id

    def write_file(self, file_path: str, table_id: str = TABLE_ID):
        """Write comments into the BigQuery table specified by table_id.

        :param file_path: path to file to load to database
        :param table_id: id of the table to write into
        """
        # create a dataset reference
        dataset_ref = self.client.dataset(self.dataset_id)

        # create destiny table reference
        table_ref = dataset_ref.table(table_id)

        # create temporary table
        schema_path = 'schemas/' + table_id + '.json'
        schema = self.client.schema_from_json(schema_path)
        temp_table_id = self.create_table(
            f"{BIGQUERY_PROJECT_ID}.{BIGQUERY_DATASET_ID}.{table_id}",
            schema,
            expiracy_hours=1
        )

        # create a load job config
        load_job_config = LoadJobConfig()
        load_job_config.source_format = SourceFormat.NEWLINE_DELIMITED_JSON
        load_job_config.autodetect = True

        # load the data
        job = self.client.load_table_from_file(
            open(file_path, "rb"), temp_table_id, job_config=load_job_config
        )
        job.result()

    def update_comments(self, comments: list[Comment]):
        """Update comments in database.

        :param comments: comments to update"""
        for comment in comments:
            self.update_comment(comment)

    def update_comment(self, comment: Comment) -> None:
        """Update comment in database.

        :param comment: comment to update
        """
        # TODO
        pass
