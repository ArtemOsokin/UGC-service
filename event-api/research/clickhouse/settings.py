from datetime import datetime
from functools import wraps

from clickhouse_driver import Client

client = Client(host='localhost')

insert = 'INSERT INTO test_base.test VALUES'


def time_run_func(func):
    @wraps(func)
    def inner(*args, **kwargs):
        start_time = datetime.now()
        try:
            return func(*args, **kwargs)
        finally:
            print('Time:', datetime.now() - start_time)

    return inner
