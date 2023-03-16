from typing import Any
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
import uvicorn
from datetime import datetime

import spacy
import uuid

from src.auth.auth_bearer import JWTBearer
from src.api.response_models import (
    RecognitionResponse,
    ErrorCode,
    BaseResponse,
    LatestMentionsResponse,
)
from src.api.request_models import (
    ExtractorRequestBody,
    MDRUpdateRequest,
    BRUpdateRequest,
    FeedbackRequest,
)
from src.models import Comment, MediaHouse, Status
from src.tools import write_jsonlines_to_bucket, check_expiration_time
from src.finder import ModelType, find_mention
from src.mdr.preprocess import preprocess_mdr_comment
from src.mdr.get_comments import MDRCommentGetter
from src.br.get_comments import BRCommentGetter
from src.br.preprocess import preprocess_br_comment
from src.publisher.teams import TeamsConnector, send_comments
from src.storage.postgres import (
    create_tables,
    get_engine,
    TableWriter,
    sessionmaker,
    get_unpublished,
    get_unprocessed,
    get_latest_mentions,
)
from settings import BUGG_MODEL_V1_PATH, BACKUP_PATH, POSTGRES_URI, MAX_NUMBER_PUBLISH
from src.exceptions import PreprocessingError

ENGINE = get_engine(POSTGRES_URI)
SPACY_MODEL = spacy.load(BUGG_MODEL_V1_PATH)
APP = FastAPI(
    title="WTWM mention extractor",
    description="Recognise mentions of the editorial team in a given text.",
    version="0.0.1",
)

ORIGINS = [
    "https://interaktiv.brdata-dev.de",
    "https://interaktiv.br.de",
    "http://localhost:8080",
    "http://localhost",
    "http://0.0.0.0:8080",
    "http://0.0.0.0",
]

APP.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
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
@APP.post(
    "/v1/find_mentions",
    response_model=RecognitionResponse,
    dependencies=[Depends(JWTBearer())],
)
async def find_mentions(body: ExtractorRequestBody) -> RecognitionResponse:
    """Find mentions of the editorial team in a comment."""
    type_ = ModelType.GPT2
    results = find_mention(
        type_,
        body.text,
        str(uuid.uuid4()),
    )
    if len(results) > 1:
        msg = f"Found {len(results)} mentions."
    elif len(results) == 1:
        msg = f"Found {len(results)} mentioning."
    else:
        msg = "Found no mentions."

    return RecognitionResponse(
        status="ok", msg=msg, result=[r.as_dict() for r in results]
    )


@APP.get(
    "/v1/get_mdr_comments",
    response_model=BaseResponse,
    dependencies=[Depends(JWTBearer())],
)
def update_comments_from_mdr(
    query: dict[str, Any] = Depends(MDRUpdateRequest.query_template)
) -> BaseResponse:
    """Get comments from mdr source, store them in the bucket and db."""
    config = MDRUpdateRequest.from_query(query)
    get_comments = MDRCommentGetter()
    # postgres credentials
    create_tables(ENGINE)
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
    with TableWriter(ENGINE, purge=False) as writer:
        for comment in comments:
            writer.write(comment)

    msg = f"Processed {len(comments)} comments."
    return BaseResponse(status="ok", msg=msg)


@APP.get(
    "/v1/get_latest_br_comments",
    response_model=BaseResponse,
    dependencies=[Depends(JWTBearer())],
)
def get_latest_br_comments(
    query: dict[str, Any] = Depends(BRUpdateRequest.query_template)
) -> BaseResponse:
    """Get comments from mdr source, store them in the bucket and db."""
    config = BRUpdateRequest.from_query(query)
    get_comments = BRCommentGetter()
    # postgres credentials
    create_tables(ENGINE)
    # process comments
    comments = []
    for raw_comment in get_comments(config.lookback):
        try:
            comment = Comment(**preprocess_br_comment(raw_comment))
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
    with TableWriter(ENGINE, purge=False) as writer:
        for comment in comments:
            writer.write(comment)

    msg = f"Processed {len(comments)} comments."
    return BaseResponse(status="ok", msg=msg)


@APP.get(
    "/v1/add_mentions_to_stored_comments",
    response_model=BaseResponse,
    dependencies=[Depends(JWTBearer())],
)
def add_mentions_to_stored_comments() -> BaseResponse:
    """Add extraction result to unprocessed comments."""
    session = sessionmaker()(bind=ENGINE)
    comments = get_unprocessed(session)
    mentions = []
    type_ = ModelType.GPT2
    for comment in comments:
        try:
            results = find_mention(type_, comment.body, comment.id)
        except PreprocessingError as exc:
            print(f"Caught exception for comment with id: '{comment.id}': {exc}")
            comment.status = Status.ERROR
            comment.note = str(exc)
        else:
            if results:
                comment.status = Status.TO_BE_PUBLISHED
                comment.mentions = results
                mentions.extend(results)
            else:
                comment.status = Status.NO_MENTIONS

    with TableWriter(ENGINE, session=session, purge=False) as writer:
        for comment in comments:
            writer.update(comment)

    session.close()
    msg = f"Processed and updated {len(comments)} comments."
    return BaseResponse(status="ok", msg=msg)


@APP.get(
    "/v1/send_comments_to_teams",
    response_model=BaseResponse,
    dependencies=[Depends(JWTBearer())],
)
def send_comments_to_teams() -> BaseResponse:
    """Get unsend comments and publish them to teams."""
    session = sessionmaker()(bind=ENGINE)
    unpublished_comments = get_unpublished(session)
    if not unpublished_comments:
        msg = "No new comments to publish."
        return BaseResponse(status="ok", msg=msg)

    lookback_minutes = 30
    unpublished_comments = check_expiration_time(unpublished_comments, lookback_minutes)
    with TableWriter(ENGINE, session=session, purge=False) as writer:
        for media_house_id in ["mdr", "br"]:
            connector = TeamsConnector(MediaHouse.from_id(media_house_id))
            # TODO switch back to media house related publishing. Now all comments are published to each media house
            send_comments(connector, unpublished_comments, writer, MAX_NUMBER_PUBLISH)

        # TODO set back to count per media house
        pub_buf = len(unpublished_comments)

        # 'YourArgument' project publication
        connector = TeamsConnector(MediaHouse.from_id("your_argument"))
        send_comments(
            connector,
            [c for c in unpublished_comments if c.media_house == MediaHouse.BR],
            writer,
            MAX_NUMBER_PUBLISH,
        )

    session.close()
    msg = f"Published {pub_buf} comments."
    return BaseResponse(status="ok", msg=msg)


@APP.get(
    "/v1/get_latest_mentions",
    response_model=LatestMentionsResponse,
    dependencies=[Depends(JWTBearer())],
)
def get_mentions() -> LatestMentionsResponse:
    """Return a list of the latest comments with mentions."""
    session = sessionmaker()(bind=ENGINE)
    latest_mentions = get_latest_mentions(session)
    session.close()
    if not latest_mentions or latest_mentions is None:
        msg = "No comments with mentions lately."
        return LatestMentionsResponse(status="ok", msg=msg, result=[])

    msg = f"Found {len(latest_mentions)} comments with mentions."
    return LatestMentionsResponse(status="ok", msg=msg, result=latest_mentions)


@APP.get(
    "/v1/feedback", response_model=BaseResponse, dependencies=[Depends(JWTBearer())]
)
def give_feedback(
    query: dict[str, Any] = Depends(FeedbackRequest.query_template)
) -> BaseResponse:
    """Reload a model from the bucket into this running API."""
    try:
        config = FeedbackRequest.from_query(query)
    except (TypeError, ValueError) as exc:
        msg = f"Query is illformed: '{exc}'"
        raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=msg)
    else:
        session = sessionmaker()(bind=ENGINE)
        with TableWriter(ENGINE, session=session, purge=False) as writer:
            comment = writer.get_comment(config.id)
            if comment is None:
                msg = f"No comment with id: '{config.id}'"
                raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=msg)

            comment.status = config.choice
            writer.update(comment)

        session.close()
        return BaseResponse(status="ok", msg=f"Updated comment status with feedback.")


@APP.get(
    "/v1/reload_model", response_model=BaseResponse, dependencies=[Depends(JWTBearer())]
)
def reload_model() -> BaseResponse:
    """Reload a model from the bucket into this running API."""
    try:
        SPACY_MODEL = spacy.load(BUGG_MODEL_V1_PATH)
    except OSError as exc:
        msg = f"Couldn't find the model at: '{BUGG_MODEL_V1_PATH}' because '{exc}'"
        raise HTTPException(status_code=ErrorCode.NOT_FOUND.value, detail=msg)
    else:
        return BaseResponse(
            status="ok", msg=f"Successfully reloaded model '{BUGG_MODEL_V1_PATH}'"
        )


if __name__ == "__main__":
    uvicorn.run(APP, host="0.0.0.0", port=3000)
