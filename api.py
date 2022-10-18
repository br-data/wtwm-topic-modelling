from typing import Any
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
import uvicorn
from datetime import datetime

import spacy

from src.api.response_models import ExtractorResponse, ErrorCode, BaseResponse
from src.api.request_models import ExtractorRequestBody, MDRUpdateRequest
from src.models import Comment
from src.tools import write_jsonlines_to_bucket
from src.extract import extract_mentions_from_text
from src.storage.big_query import BigQueryWriter
from src.mdr.get_comments import MDRCommentGetter
from src.mdr.preprocess import preprocess_mdr_comment
from settings import MODEL_PATH, BACKUP_PATH, TABLE_ID

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
def update_comments_from_mdr(
    query: dict[str, Any] = Depends(MDRUpdateRequest.query_template)
) -> None:
    """Get comments from mdr source, store them in the bucket and db."""
    config = MDRUpdateRequest.from_query(query)
    get_comments = MDRCommentGetter()
    comments = []
    for raw_comment in get_comments(config.from_, config.to):
        try:
            comment = Comment(**preprocess_mdr_comment(raw_comment))
        except (IndexError, AttributeError, KeyError, ValueError) as exc:
            print(f"Skipping comment because of: {exc}")
        else:
            comments.append(comment)

    # save raw comments as backup
    file_path = BACKUP_PATH + f"{datetime.now().isoformat()}_comment_backup.jsonl"
    write_jsonlines_to_bucket(file_path, [c.as_dict() for c in comments])
    # TODO when needed
    # raw_comments = load_comments_from_bucket(path)
    writer = BigQueryWriter()
    writer.write_file(file_path, TABLE_ID)
    msg = f"Got, stored and wrote {len(comments)} comments."
    return BaseResponse(status="ok", msg=msg)


# @APP.post("/v1/update_comments_from_br")
# def update_comments_from_br() -> None:
#    raw_comments = get_raw_comments_from_br()
#    write_comments_to_bucket(path, raw_comments)
#    #raw_comments = load_comments_from_bucket(path)
#    comments = preprocess_br_comments(raw_comments)
#    _write_data_to_database(comments)
#
# @APP.post("/v1/to_database")
# def write_data_to_database(*args, **kwargs) -> None:
#    """Take the comments and write them to big query."""
#    comments = process request(*args, **kwargs)
#    _write_data_to_database(file_buff.behave_like_a_file())
#
#
# def _write_data_to_database(comments):
#    file_buff = io(comments)
#    # do write
#
# @APP.post("/v1/update_db")
# def update_db(*args, **kwargs) -> None:
#    # comments = get new comments from db
#    # find_mentions(comments)
#    # update_comments_in_db(comments)
#
# @APP.post("/v1/send_comments_to_teams")
# def send_comments_to_teams(*args, **kwargs) -> None:
#    # unsend = get_unsend_comments_from_db()
#    # response = send_comments_to_teams(unsend)
#    # sent = []
#    # for result, comment in zip(unsend, result):
#        # mark_as_send(comment)
#        # add_feedback(comment, result)
#        # sent.append(comment)
#
#    # update_comments_in_db(sent)

# @APP.post("/v1/generate_train_corpus")
# def generate_train_corpus() -> None:
#    pass


@APP.get("/v1/reload_model", response_model=BaseResponse)
def reload_model() -> None:
    """Reload a model from the bucket into this running API."""
    try:
        SPACY_MODEL = spacy.load(MODEL_PATH)
    except OSError as exc:
        msg = f"Couldn't find the model at: '{MODEL_PATH}' because '{exc}'"
        raise HTTPException(status_code=ErrorCode.MODEL_NOT_FOUND.value, detail=msg)
    else:
        return BaseResponse(
            status="ok", msg=f"Successfully reloaded model '{MODEL_PATH}'"
        )


if __name__ == "__main__":
    uvicorn.run(APP, host="0.0.0.0", port=3000)
