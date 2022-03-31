import logging
import sqlite3
from contextlib import contextmanager

sqlite_conn_log = logging.getLogger("db_connector")


@contextmanager
def conn_content(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    except sqlite3.Error:
        sqlite_conn_log.error("Exception occurred", exc_info=True)
    finally:
        conn.close()


if __name__ == '__main__':
    pass
