import logging
import psycopg2
import sqlite3

from psycopg2 import sql
from psycopg2.extensions import connection as _connection
from psycopg2.extras import execute_values

module_log = logging.getLogger("sqlite_to_postgres.load_data")


class SQLiteLoader:
    """The main class of interaction with the SQLite database"""
    def __init__(self, conn, batch_size: int):
        """
        Init connection
        """
        self.conn = conn
        self.batch_size = batch_size
        self.cursor = self.conn.cursor()

    def extract_data_from(self, query: str) -> sqlite3.Row:
        """
        Retrieves data from the specified database table.
        The composition and order of the fields is determined
        through the data class passed to the function
        :return sqlite3.Row object
        """
        try:
            self.cursor.execute(query)
        except sqlite3.Error:
            module_log.error("Exception occurred", exc_info=True)
        while True:
            rows = self.cursor.fetchmany(size=self.batch_size)
            if not rows:
                break
            yield from rows


class PostgresSaver:
    """The main class of interaction with the PostgreSQL database"""
    def __init__(self, conn):
        """
        Init connection
        """
        self.conn = conn
        self.cursor = self.conn.cursor()

    def save_all_data(self, query, data, page_size):
        """
        Save data to a table in blocks by page_size rows
        Use function psycopg2.extras.execute_values()
        Execute a statement using VALUES with a sequence of parameters.
        :return None
        """
        try:
            execute_values(self.cursor, query, data, page_size=page_size)
            return
        except (Exception, psycopg2.DatabaseError):
            module_log.error("Exception occurred", exc_info=True)

    def execute_query_wo_data(self, query):
        """
        Executes an SQL query that does not require additional parameters or data
        :return: None
        """
        try:
            self.cursor.execute(query)
            return
        except (Exception, psycopg2.DatabaseError):
            module_log.error("Exception occurred", exc_info=True)


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection, tables: tuple, data_struct: tuple, batch_size: int):
    """The main method of loading data from SQLite to Postgres"""
    try:
        sqlite_loader = SQLiteLoader(connection, batch_size=batch_size)
        postgres_saver = PostgresSaver(pg_conn)

        module_log.info('Preparing a table cleanup request')
        clear_query_pg = sql.SQL("TRUNCATE {}").format(
            sql.SQL(', ').join([sql.Identifier(table) for table in tables]))

        module_log.info('Executing a table deletion request...')
        postgres_saver.execute_query_wo_data(clear_query_pg)
        module_log.info(f'Tables {tables} cleared')

        for table, data_structure in zip(tables, data_struct):
            columns = [attr for attr in data_structure.__annotations__.keys()]

            module_log.info(f'Preparing a query to fetch data from table "{table}" in the SQLite database...')
            raw_query_sqlite = sql.SQL("SELECT {fields} FROM {table}").format(
                fields=sql.SQL(", ").join([sql.Identifier(field) for field in columns]),
                table=sql.Identifier(table))
            query_sqlite = raw_query_sqlite.as_string(pg_conn)

            module_log.info(f'Extracting data from table "{table}" in the SQLite database in batches of {batch_size} records')
            data = sqlite_loader.extract_data_from(query_sqlite)
            module_log.info(f'Preparing a query to insert data into a table "{table}" in a PostgreSQL database...')
            save_query = sql.SQL("INSERT INTO {table} ({fields}) VALUES %s").format(
                table=sql.Identifier(table),
                fields=sql.SQL(', ').join([sql.Identifier(field) for field in columns])
            )
            module_log.info(f'Saving data to a table "{table}" in a PostgreSQL database in batches of {batch_size} records...')
            rows = []
            count, total = 0, 0
            for row in data:
                rows.append(row)
                count += 1
                if count >= 500:
                    postgres_saver.save_all_data(save_query, rows, page_size=batch_size)
                    total += len(rows)
                    module_log.info(f'{len(rows)} records are written to the "{table}" table')
                    rows = []
                    count = 0

            postgres_saver.save_all_data(save_query, rows, page_size=batch_size)
            module_log.info(f'{len(rows)} records are written to the "{table}" table')

            total += len(rows)
            module_log.info(f'There are total {total} records written to table "{table}"')
        return
    except (Exception, psycopg2.DatabaseError, sqlite3.DatabaseError):
        module_log.error("Exception occurred", exc_info=True)


if __name__ == '__main__':
    pass
