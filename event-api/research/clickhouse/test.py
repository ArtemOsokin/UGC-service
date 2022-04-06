from datetime import datetime
import random
from settings import (client,
                      insert,
                      time_run_func)


@time_run_func
def test_insert():
    data = []
    for i in range(10000000, 10000100):
        row = {
            'id': i,
            'user_id': random.randint(1501, 1700),
            'movies_id': random.randint(20202, 20303),
            'movie_mark': random.randint(1, 360),
            'event_time': datetime.now()
        }
        data.append(row)
    client.execute(insert, data)


@time_run_func
def test_select():
    client.execute('SELECT count() FROM test_base.test')
    client.execute('SELECT movie_mark FROM test_base.test')
    client.execute('SELECT * FROM test_base.test WHERE user_id=300')
    client.execute('SELECT sum(movies_id) FROM test_base.test')


def main():
    test_insert()
    test_select()


if __name__ == '__main__':
    main()
