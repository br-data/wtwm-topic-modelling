from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
import uvicorn

import spacy

from src.api.response_models import ExtractorResponse, ErrorCode, BaseResponse
from src.api.request_models import ExtractorRequestBody
from src.extract import extract_mentions_from_text
from settings import MODEL_PATH


SPACY_MODEL = spacy.load(MODEL_PATH)
APP = FastAPI(
    title="WTWM mention extractor",
    description="Extract mentions of the editorial team from a given text.",
    version="0.0.1",
)
APP.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://interaktiv.brdata-dev.de",
        "https://interaktiv.br.de",
        "http://0.0.0.0:3000",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@APP.get("/")
async def redirect():
    """Redirect to documentation if index page is called."""
    response = RedirectResponse(url="/docs")
    return response


# Note: Security is done by the dev server for now
@APP.post("/v1/find_mentions", response_model=ExtractorResponse)
async def find_mentions(body: ExtractorRequestBody) -> ExtractorResponse:
    """Extract mentions of the editorial team in a comment."""
    result = extract_mentions_from_text(SPACY_MODEL, body.text)
    if len(result) > 1:
        msg = f"Found {len(result)} mentions."
    elif len(result) == 1:
        msg = f"Found {len(result)} mentioning."
    else:
        msg = "Found no mentions."

    return ExtractorResponse(status="ok", msg=msg, result=result)


@APP.get("/v1/get_mdr_comments", response_model=BaseResponse)
def update_comments_from_mdr() -> None:
    """Get comments from mdr source, store them in the bucket and db."""
    #raw_comments = get_raw_comments_from_mdr()
    # get new new comments from mdr
    # save comments to file in standard comment format
    #write_comments_to_bucket(path, comments)
    # raw_comments = load_comments_from_bucket(path)
    #comments = preprocess_mdr_comments(raw_comments)
    #_write_data_to_database(comments)
    comments = []
    msg = f"Got, stored and wrote {len(comments)} comments."
    return BaseResponse(status="ok", msg=msg)


@APP.get("/v1/reload_model", response_model=BaseResponse)
def reload_model() -> None:
    """Reload a model from the bucket into this running API."""
    try:
        SPACY_MODEL = spacy.load(MODEL_PATH)
    except OSError as exc:
        msg = f"Couldn't find the model at: '{MODEL_PATH}' because '{exc}'"
        raise HTTPException(status_code=ErrorCode.MODEL_NOT_FOUND.value, detail=msg)
    else:
        return BaseResponse(status="ok", msg=f"Successfully reloaded model '{MODEL_PATH}'")


if __name__ == "__main__":
    uvicorn.run(APP, host="0.0.0.0", port=3000)
