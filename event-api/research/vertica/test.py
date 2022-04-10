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
        for _ in range(10000):
            row = (
                random.randint(1, 1500),
                random.randint(1, 20000),
                random.randint(1, 360),
                datetime.now()
            )
            data.append(row)
        cursor.executemany('INSERT INTO test (user_id, movie_id, movie_mark, event_time) VALUES (?,?,?,?)', data)


@time_run_func
def test_select_count():
    with vertica_python.connect(**dsl) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM test')


@time_run_func
def test_select_by_movie_mark():
    with vertica_python.connect(**dsl) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT movie_mark FROM test')


@time_run_func
def test_select_count_by_user_id_300():
    with vertica_python.connect(**dsl) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM test WHERE user_id=300')


@time_run_func
def test_select_sum():
    with vertica_python.connect(**dsl) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT SUM(movie_id) FROM test')


def main():
    test_insert()
    test_select_count()
    test_select_by_movie_mark()
    test_select_count_by_user_id_300()
    test_select_sum()


if __name__ == '__main__':
    main()
