import os

# file path
MODEL_PATH = os.environ.get("MODEL_PATH", "model/detect_mentions/")
BACKUP_PATH = os.environ.get("BACKUP_PATH", "model/backup/")

# recogniser source data
BASELINE_SOURCE = os.environ.get("BASELINE_SOURCE_FILE", "model/baseline_regex_collection.txt")
PATTERN_RECOGNISER_SOURCE = os.environ.get("TRIE_PATTERN_SOURCE_FILE", "model/trie_patterns.txt")
MDR_COMMENT_ENDPOINT_TOKEN = os.environ["MDR_COMMENT_ENDPOINT_TOKEN"]
MDR_COMMENT_ENDPOINT = os.environ["MDR_COMMENT_ENDPOINT"]
BR_COMMENT_ENDPOINT_TOKEN = os.environ["BR_COMMENT_ENDPOINT_TOKEN"]
BR_COMMENT_ENDPOINT = os.environ["BR_COMMENT_ENDPOINT"]
BIGQUERY_PROJECT_ID = "journalismai-362410"
BIGQUERY_CREDENTIAL_PATH = os.environ.get(
    "IDA_BIGQUERY_CREDENTIAL_PATH", "data/journalismai-credentials.json"
)
BIGQUERY_DATASET_ID = "wtwm"
TABLE_ID = os.environ.get("TABLE_ID", "comments")
# test target for teams channel publication
# TODO add feedback channel address
TEST_FEEDBACK_TARGET = "TODO"
MDR_FEEDBACK_TARGET = "TODO"

# postgres
POSTGRES_IP = os.environ["DATABASE_ADDRESS"]
POSTGRES_USER = os.environ["DATABASE_USER"]
POSTGRES_PASS = os.environ["DATABASE_PASSWORD"]
POSTGRES_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_IP}"

# team settings
MAX_NUMBER_PUBLISH = 5
TEST_TARGET = os.environ["TEST_TARGET"]
MDR_TARGET = os.environ["MDR_TARGET"]
BR_TARGET = os.environ["BR_TARGET"]
