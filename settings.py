import os

MODEL_PATH = os.environ.get("MODEL_PATH", "model/detect_mentions/")
BACKUP_PATH = os.environ.get("BACKUP_PATH", "model/backup/")
MDR_COMMENT_ENDPOINT_TOKEN = os.environ.get("MDR_COMMENT_ENDPOINT_TOKEN", ".credentials/coral-talk-token.json")
MDR_COMMENT_ENDPOINT = os.environ.get("MDR_COMMENT_ENDPOINT", "./credentials/coral-talk-endpoint.json")
BIGQUERY_PROJECT_ID = "journalismai-362410"
BIGQUERY_CREDENTIAL_PATH = os.environ.get(
    "IDA_BIGQUERY_CREDENTIAL_PATH", "data/journalismai-credentials.json"
)
BIGQUERY_DATASET_ID = "wtwm"
TABLE_ID = os.environ.get("TABLE_ID", "test_table")
