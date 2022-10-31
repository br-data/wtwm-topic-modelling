from typing import Any
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
import uvicorn
from datetime import datetime
from collections import defaultdict

import spacy
import uuid

from src.api.response_models import ExtractorResponse, ErrorCode, BaseResponse
from src.api.request_models import ExtractorRequestBody, MDRUpdateRequest
from src.models import Comment, MediaHouse, ExtractionType, Status
from src.tools import write_jsonlines_to_bucket
from src.extract import extract_mentions_from_text
from src.mdr.preprocess import preprocess_mdr_comment
from src.mdr.get_comments import MDRCommentGetter
from src.publisher.teams import TeamsConnector, send_comments
from src.storage.postgres import create_tables, get_engine, TableWriter, sessionmaker, get_unpublished, get_unprocessed
from settings import MODEL_PATH, BACKUP_PATH, POSTGRES_URI

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
    result = extract_mentions_from_text(SPACY_MODEL, str(uuid.uuid1()), body.text, extracted_from=ExtractionType.SPACY_MODEL_A)
    if len(result) > 1:
        msg = f"Found {len(result)} mentions."
    elif len(result) == 1:
        msg = f"Found {len(result)} mentioning."
    else:
        msg = "Found no mentions."

    return ExtractorResponse(status="ok", msg=msg, result=[r.as_dict() for r in result])


@APP.get("/v1/get_mdr_comments", response_model=BaseResponse)
def update_comments_from_mdr(
    query: dict[str, Any] = Depends(MDRUpdateRequest.query_template)
) -> BaseResponse:
    """Get comments from mdr source, store them in the bucket and db."""
    config = MDRUpdateRequest.from_query(query)
    get_comments = MDRCommentGetter()
    # postgres credentials
    engine = get_engine(POSTGRES_URI)
    create_tables(engine)
    # process comments
    comments = []
    for raw_comment in get_comments(config.from_, config.to):
        try:
            comment = Comment(**preprocess_mdr_comment(raw_comment))
        except (IndexError, AttributeError, KeyError, ValueError) as exc:
            print(f"Skipping comment because of: {exc}")
        else:
            comments.append(comment)

    ## save raw comments as backup
    file_path = BACKUP_PATH + f"{datetime.now().isoformat()}_comment_backup.jsonl"
    write_jsonlines_to_bucket(file_path, [c.as_dict() for c in comments])
    # TODO when needed
    # raw_comments = load_comments_from_bucket(path)
    # write to database
    with TableWriter(engine, purge=False) as writer:
        for comment in comments:
            writer.update(comment)

    msg = f"Got, stored and wrote {len(comments)} comments."
    return BaseResponse(status="ok", msg=msg)


@APP.get("/v1/add_mentions_to_stored_comments", response_model=BaseResponse)
def add_mentions_to_stored_comments() -> BaseResponse:
    """Add extraction result to unprocessed comments."""
    engine = get_engine(POSTGRES_URI)
    session = sessionmaker()(bind=engine)
    comments = get_unprocessed(session)
    mentions = []
    for comment in comments:
        result = extract_mentions_from_text(
            SPACY_MODEL,
            comment.id,
            comment.body,
            extracted_from=ExtractionType.SPACY_MODEL_A
        )
        if result:
            comment.status = Status.TO_BE_PUBLISHED
            comment.mentions = result
            mentions.extend(result)
        else:
            comment.status = Status.NO_MENTIONS

    with TableWriter(engine, session=session, purge=False) as writer:
        # take care to first write the mentions to have a db entry to reference from the comment
        for mention in mentions:
            writer.update(mention)

        for comment in comments:
            writer.update(comment)

    msg = f"Processed and updated {len(comments)} comments."
    return BaseResponse(status="ok", msg=msg)


@APP.get("/v1/send_comments_to_teams", response_model=BaseResponse)
def send_comments_to_teams() -> BaseResponse:
    """Get unsend comments and publish them to teams."""
    engine = get_engine(POSTGRES_URI)
    session = sessionmaker()(bind=engine)
    comments = get_unpublished(session)
    if not comments:
        msg = "No new comments to publish."
        return BaseResponse(status="ok", msg=msg)

    by_media_house = defaultdict(list)
    for comment in comments:
        by_media_house[comment.media_house.value].append(comment)

    pub_buf = 0
    with TableWriter(engine, session=session, purge=False) as writer:
        for media_house_id, comments in by_media_house.items():
            connector = TeamsConnector(MediaHouse.from_id(media_house_id))
            send_comments(connector, comments, writer)
            pub_buf += len(comments)

    msg = f"Published {pub_buf} comments."
    return BaseResponse(status="ok", msg=msg)


@APP.get("/v1/reload_model", response_model=BaseResponse)
def reload_model() -> BaseResponse:
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
