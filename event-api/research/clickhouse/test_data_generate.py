import random
from datetime import datetime
from settings import (client,
                      insert,
                      time_run_func)


@time_run_func
def main():
    data = []
    for i in range(10000000):
        row = {
            'id': i,
            'user_id': random.randint(1, 1500),
            'movies_id': random.randint(1, 20000),
            'movie_mark': random.randint(1, 360),
            'event_time': datetime.now()
        }
        data.append(row)

        if len(data) >= 1000:
            client.execute(insert, data)
            data = []


if __name__ == '__main__':
    main()
