from typing import Any, Optional, Union

from sqlalchemy.engine.base import Connection, Engine  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore
from sqlalchemy.exc import OperationalError  # type: ignore
from sqlalchemy import (create_engine, and_)  # type: ignore
from src.models import BASE, Comment, ExtractorResult, Status


SESSION = sessionmaker()
POSTGRES_ENTRY_TYPES = Union[Comment, ExtractorResult]


class PSQLWriter:
    def __init__(
        self,
        engine: Engine,
        session: Optional[sessionmaker] = None,
        purge: bool = False,
    ) -> None:
        """Base class for writting items to db.
        :param engine: db communication engine
        :param session: db session
        :param purge: purge all existing entries in db
        Note: Purge can be used to ensure, that retrospective stock price
              changes a updated in db be overwritting existent values.
        """
        self._engine = engine
        self._session = session
        self._purge = purge

    def __enter__(self) -> "PSQLWriter":
        if not self._session:
            self._session = SESSION(bind=self._engine)

        if self._purge:
            self._purge_table()

        return self

    def __exit__(self, *args: list[Any]) -> None:
        if self._session is not None:
            self._session.commit()
            self._session.close()

    def _purge_table(self) -> None:
        raise NotImplementedError


class TableWriter(PSQLWriter):
    def _purge_table(self) -> None:
        """Purge table content."""
        if self._session is not None:
            self._session.query(Comment).delete()  # type: ignore
        else:
            raise ValueError("Session not initialized.")

    def write(
            self, entry: POSTGRES_ENTRY_TYPES
    ) -> None:
        """Add entry to current session.
        :param entry: entry to add
        """
        if self._session is not None:
            self._session.add(entry)
        else:
            raise ValueError("Session not initialized.")

    def update(
            self, entry: POSTGRES_ENTRY_TYPES
    ) -> None:
        """Merge entry with current session.
        :param entry: entry to merge
        """
        if self._session is not None:
            self._session.merge(entry)
        else:
            raise ValueError("Session not initialized.")


def get_engine(uri: str) -> Engine:
    """Create and return a db communication engine.
    :param uri: db ressource identifier
    """
    return create_engine(uri)


def get_connection(engine: Engine) -> Connection:
    """Open and return a db connection.
    :param engine: db communication object
    """
    try:
        conn = engine.connect()
    except OperationalError as exc:
        raise ConnectionError(f"Could not connect to postgres: {exc}")
    else:
        return conn


def create_tables(engine) -> None:
    """Create database tables."""
    BASE.metadata.create_all(engine)


def get_unpublished(session) -> list[Comment]:
    """Query the database for comments that are ready to be published.

    :param session: running postgress connection
    """

    return session\
        .query(Comment)\
        .join(ExtractorResult)\
        .filter(Comment.status == Status.TO_BE_PUBLISHED)\
        .all()


def get_unprocessed(session) -> list[Comment]:
    """Query the database for comments that are unprocessed by extraction model.

    :param session: running postgress connection
    """
    return session\
        .query(Comment)\
        .filter(Comment.status == Status.TO_BE_PROCESSED)\
        .all()

