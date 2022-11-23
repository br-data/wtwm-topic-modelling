import os

# file path
BACKUP_PATH = os.environ.get("BACKUP_PATH", "model/backup/")
GPT2_MODEL_PATH = os.environ.get("GPT2_MODEL_PATH", "model/gpt2/")
BUGG_MODEL_V1_PATH = os.environ.get("BUGG_MODEL_V1_PATH", "model/detect_mentions/")
# recogniser source data
BASELINE_SOURCE = os.environ.get(
    "BASELINE_SOURCE_FILE", "model/baseline_regex_collection.txt"
)

# comment source api settings
MDR_COMMENT_ENDPOINT_TOKEN = os.environ["MDR_COMMENT_ENDPOINT_TOKEN"]
MDR_COMMENT_ENDPOINT = os.environ["MDR_COMMENT_ENDPOINT"]
BR_COMMENT_ENDPOINT_TOKEN = os.environ["BR_COMMENT_ENDPOINT_TOKEN"]
BR_COMMENT_ENDPOINT = os.environ["BR_COMMENT_ENDPOINT"]


# postgres
TABLE_ID = os.environ.get("TABLE_ID", "comments")
POSTGRES_IP = os.environ["DATABASE_ADDRESS"]
POSTGRES_USER = os.environ["DATABASE_USER"]
POSTGRES_PASS = os.environ["DATABASE_PASSWORD"]
POSTGRES_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_IP}"

# team settings
MAX_NUMBER_PUBLISH = 5
TEST_TARGET = os.environ["TEST_TARGET"]
MDR_TARGET = os.environ["MDR_TARGET"]
BR_TARGET = os.environ["BR_TARGET"]
