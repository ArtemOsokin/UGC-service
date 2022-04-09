from datetime import datetime
from functools import wraps

dsl = {
    'host': '127.0.0.1',
    'port': 5433,
    'user': 'dbadmin',
    'password': '',
    'database': 'docker',
    'autocommit': True,
    'use_prepared_statements': True
}


def time_run_func(func):
    @wraps(func)
    def inner(*args, **kwargs):
        start_time = datetime.now()
        try:
            return func(*args, **kwargs)
        finally:
            print('Time:', datetime.now() - start_time)

    return inner
