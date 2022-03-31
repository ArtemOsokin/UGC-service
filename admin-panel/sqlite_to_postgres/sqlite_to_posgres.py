import os
import psycopg2
import logging

from dotenvy import load_env, read_file
from psycopg2.extras import DictCursor

import load_data
import db_connector
from model_data import Genre, GenreFilmWork, PersonFilmWork, Person, FilmWork


if __name__ == '__main__':
    # Set logging
    log = logging.getLogger("sqlite_to_postgres")
    log.setLevel(logging.INFO)
    fh = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    log.addHandler(fh)

    # Loading environment variables
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env.dev')
    if os.path.exists(dotenv_path):
        load_env(read_file(dotenv_path))
    dsl = {
        'dbname': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': os.environ.get('DB_HOST'),
        'port': os.environ.get('DB_PORT'),
        'options': '-c search_path=content',
    }
    sqlite_path = os.path.join(os.path.dirname(__file__), 'db.sqlite')

    # Set the tables and the names of the date classes in which the tables are described
    tables = ('film_work', 'genre', 'person', 'person_film_work', 'genre_film_work',)
    data_structures = (FilmWork, Genre, Person, PersonFilmWork, GenreFilmWork,)

    # Set batch size
    batch_size = 500

    with db_connector.conn_content(sqlite_path) as sqlite_conn, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        load_data.load_from_sqlite(sqlite_conn, pg_conn, tables, data_structures, batch_size)
