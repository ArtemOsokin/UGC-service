import random
from datetime import datetime

import vertica_python

from settings import (dsl,
                      time_run_func)


@time_run_func
def test_insert():
    with vertica_python.connect(**dsl) as connection:
        cursor = connection.cursor()
        data = []
        for _ in range(100):
            row = (
                random.randint(1, 1500),
                random.randint(1, 20000),
                random.randint(1, 360),
                datetime.now()
            )
            data.append(row)
        cursor.executemany('INSERT INTO test (user_id, movie_id, movie_mark, event_time) VALUES (?,?,?,?)', data)


@time_run_func
def test_select():
    with vertica_python.connect(**dsl) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM test')
        cursor.execute('SELECT movie_mark FROM test')
        cursor.execute('SELECT * FROM test WHERE user_id=300')
        cursor.execute('SELECT SUM(movie_id) FROM test')


def main():
    test_insert()
    test_select()


if __name__ == '__main__':
    main()
