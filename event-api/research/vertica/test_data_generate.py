import random
from datetime import datetime

import vertica_python

from settings import (dsl,
                      time_run_func)


def create_table(dsl):
    with vertica_python.connect(**dsl) as connection:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test (
            id IDENTITY,
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            movie_mark INTEGER NOT NULL,
            event_time DATETIME NOT NULL)
        ''')


@time_run_func
def generate_data(dsl):
    start = datetime.now()
    with vertica_python.connect(**dsl) as connection:
        cursor = connection.cursor()
        data = []
        count = 0
        for _ in range(10000000):
            row = (
                random.randint(1, 1500),
                random.randint(1, 20000),
                random.randint(1, 360),
                datetime.now()
            )
            data.append(row)

            if len(data) >= 1000:
                count += 1
                cursor.executemany('INSERT INTO test'
                                   ' (user_id, movie_id, movie_mark, event_time)'
                                   ' VALUES (?,?,?,?)', data)
                data = []
                print(count, ': ', datetime.now() - start)


def main(dsl):
    create_table(dsl)
    generate_data(dsl)


if __name__ == '__main__':
    main(dsl)
