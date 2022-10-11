import os
import json

try:
    ORIGINS = json.loads(os.environ["ORIGINS"])
except (KeyError, TypeError):
    raise ValueError("Missing environment variable: 'ORIGINS'")

try:
    _MODEL_PATH = os.environ["MODEL_PATH"]
except (KeyError, TypeError):
    raise ValueError("Missing environment variable: 'MODEL_PATH'")

# if deployed on server
BUCKET_PATH = os.environ.get("VOLUME_PATH", "")
MODEL_PATH = f"{BUCKET_PATH}{_MODEL_PATH}"

