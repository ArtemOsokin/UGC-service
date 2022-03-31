from contextlib import contextmanager

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import Session, declarative_base

from postgres_to_es.settings import settings

engine = create_engine(
    f'postgresql://{settings.DB.USER}:{settings.DB.PASSWORD}@localhost/{settings.DB.DBNAME}',
    echo=True,
)
engine.connect()
session = Session(bind=engine)

meta = MetaData(schema='content')
Base = declarative_base(metadata=meta)


@contextmanager
def session_scope():
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
