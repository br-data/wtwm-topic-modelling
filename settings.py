import os
import json

try:
    ORIGINS = json.loads(os.environ["ORIGINS"])
except (KeyError, TypeError):
    raise ValueError("Missing environment variable: 'ORIGINS'")

try:
    MODEL_PATH = os.environ["MODEL_PATH"]
except (KeyError, TypeError):
    raise ValueError("Missing environment variable: 'MODEL_PATH'")
