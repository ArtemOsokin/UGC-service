from datetime import datetime
import random
from settings import (client,
                      insert,
                      time_run_func)


@time_run_func
def test_insert():
    data = []
    for i in range(10000000, 10100000):
        row = {
            'id': i,
            'user_id': random.randint(1, 1500),
            'movies_id': random.randint(1, 20000),
            'movie_mark': random.randint(1, 360),
            'event_time': datetime.now()
        }
        data.append(row)

        if len(data) >= 10000:
            client.execute(insert, data)
            data = []


@time_run_func
def test_select_count():
    client.execute('SELECT count() FROM test_base.test')


@time_run_func
def test_select_by_movie_mark():
    client.execute('SELECT movie_mark FROM test_base.test')


@time_run_func
def test_select_count_by_user_id_300():
    client.execute('SELECT * FROM test_base.test WHERE user_id=300')


@time_run_func
def test_select_sum():
    client.execute('SELECT sum(movies_id) FROM test_base.test')


def main():
    test_insert()
    test_select_count()
    test_select_by_movie_mark()
    test_select_count_by_user_id_300()
    test_select_sum()


if __name__ == '__main__':
    main()
