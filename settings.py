import os

MODEL_PATH = os.environ.get("MODEL_PATH", "model/detect_mentions/")
BACKUP_PATH = os.environ.get("BACKUP_PATH", "model/backup/")
MDR_COMMENT_ENDPOINT_TOKEN = os.environ.get("MDR_COMMENT_ENDPOINT_TOKEN")
MDR_COMMENT_ENDPOINT = os.environ.get("MDR_COMMENT_ENDPOINT")
