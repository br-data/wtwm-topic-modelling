import os
import json

try:
    ORIGINS = os.environ["ORIGINS"]
except (KeyError, TypeError):
    raise ValueError("Missing environment variable: 'ORIGINS'")
else:
    if ORIGINS is None:
        ORIGINS = [
            "https://interaktiv.brdata-dev.de",
            "https://interaktiv.br.de",
            "http://0.0.0.0:3000",
            "http://localhost",
        ]
    else:
        ORIGINS = json.loads(ORIGINS)

try:
    _MODEL_PATH = os.environ["MODEL_PATH"]
except (KeyError, TypeError):
    raise ValueError("Missing environment variable: 'MODEL_PATH'")

# if deployed on server
BUCKET_PATH = os.environ.get("VOLUME_PATH", "")
MODEL_PATH = f"{BUCKET_PATH}{_MODEL_PATH}"
