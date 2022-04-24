import asyncio
import logging
import random
from logging import config as logging_config

import aioch
from benchmark_db.clickhouse.settings import settings
from benchmark_db.logger import LOGGING_CONFIG
from benchmark_db.timer import Timer
from benchmark_db.utils import ping_host

logging_config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

COUNT_RUN_QUERY = 1000  # Количество запросов к базе данных для оценки среднего времени

hosts = settings.CH.HOSTS


async def benchmark_get_list_bookmarks(count: int = 100) -> float:
    """Функция оценки времени получения списка закладок (списка film_id добавленных в закладки фильмов)
    :param count: Количество запросов в базу данных для вычисления среднего значения времени запроса.
    :return: Среднее значение времени выполнения запроса.
    """
    client = aioch.Client(
        host=settings.CH.HOSTS[0],
        port=settings.CH.PORT,
        user=settings.CH.USER,
        password=settings.CH.PASSWORD,
        ca_certs=settings.CH.CACERT,
        secure=True,
    )
    logger.info('Start process measurement of benchmarks get list bookmarks')
    func_timer = Timer('get_list_bookmarks', logger=None)
    func_timer.start()
    # Определяем общее количество уникальных пользователей, имеющих фильмы в закладках и создаем список
    # из равномерно распределенных значений user_id общим количеством равным count.
    total_user_id = await client.execute('SELECT count(DISTINCT user_id) FROM films_bookmarks')
    logger.info(total_user_id)
    step = total_user_id[0][0] // count
    list_user_id = []
    for offset in range(0, count * step, step):
        user_id = await client.execute(
            f'SELECT user_id FROM films_bookmarks LIMIT 1 OFFSET {offset}'
        )
        list_user_id.append(user_id[0][0])
    logger.debug('Got following list user_id: %s', list_user_id)
    # По полученному списку значений user_id выполняем запросы к базе данных и оцениваем среднее время
    # выполнения запросов
    timer = Timer(name='bookmarks', logger=None)
    counter = 0
    logger.debug('Start iterating on list user_id...')
    for user_id in list_user_id:
        query = f"SELECT film_id FROM films_bookmarks WHERE user_id == '{user_id}'"
        timer.start()
        result = await client.execute(query)
        elapsed_time = timer.stop()
        counter += 1
        logger.debug(
            'Elapsed time [%s] for result query #%s for benchmark_get_list_bookmarks: %s',
            elapsed_time,
            counter,
            result,
        )
    average_time = timer.timers['bookmarks'] / counter
    func_timer.stop()
    total_func_time = func_timer.timers['get_list_bookmarks']
    logger.info(
        """End process measurement of benchmarks get list bookmarks.
        Total time: %s sec. Average time: %s sec. Count query: %s.""",
        total_func_time,
        average_time,
        counter,
    )
    return average_time


async def benchmark_get_average_rating(count: int = 100) -> float:
    """Функция оценки среднего времени получения средней пользовательской оценки
    и количества лайков и дизлайков у фильма.
    :param count: Количество запросов в базу данных для вычисления среднего значения времени запроса.
    :return: Среднее значение времени выполнения запроса.
    """
    client = aioch.Client(
        host=settings.CH.HOSTS[1],
        port=settings.CH.PORT,
        user=settings.CH.USER,
        password=settings.CH.PASSWORD,
        ca_certs=settings.CH.CACERT,
        secure=True,
    )
    logger.info('Start process measurement of benchmarks get average rating movies')
    func_timer = Timer('get_average_rating', logger=None)
    func_timer.start()
    list_film_id = await client.execute('SELECT DISTINCT film_id FROM films_likes')
    logger.debug('Got following list film_id: %s', list_film_id)
    timer = Timer('average_rating', logger=None)
    counter = 0
    logger.debug('Start iterating on list film_id...')
    for film_id, *_ in random.choices(list_film_id, k=count):
        query = (
            f'SELECT '
            f"avgIf(user_rating, film_id ='{film_id}') AS average_rating,"
            f"sumIf(is_like, film_id ='{film_id}') AS count_likes,"
            f"sumIf(is_dislike, film_id = '{film_id}') AS count_dislikes "
            f'FROM films_likes'
        )
        timer.start()
        result = await client.execute(query)
        elapsed_time = timer.stop()
        counter += 1
        logger.debug(
            'Elapsed time [%s] for result query #%s for benchmark_get_average_rating: %s',
            elapsed_time,
            counter,
            result,
        )
    average_time = timer.timers['average_rating'] / counter
    func_timer.stop()
    total_func_time = func_timer.timers['get_average_rating']
    logger.info(
        """End process measurement of benchmarks get average rating movies.
        Total time: %s sec. Average time: %s sec. Count query: %s.""",
        total_func_time,
        average_time,
        counter,
    )
    return average_time


async def benchmark_get_list_favorite_films(count: int = 100) -> float:
    """Функция оценки среднего времени получения списка понравившихся пользователю фильмов.
    :param count: Количество запросов в базу данных для вычисления среднего значения времени запроса.
    :return: Среднее значение времени выполнения запроса.
    """
    client = aioch.Client(
        host=settings.CH.HOSTS[2],
        port=settings.CH.PORT,
        user=settings.CH.USER,
        password=settings.CH.PASSWORD,
        ca_certs=settings.CH.CACERT,
        secure=True,
    )
    logger.info('Start process measurement of benchmarks get list favorite films')
    func_timer = Timer('get_list_favorite_films', logger=None)
    func_timer.start()
    # Определяем общее количество уникальных пользователей, имеющих фильмы в закладках и создаем список
    # из равномерно распределенных значений user_id общим количеством равным count.
    total_user_id = await client.execute('SELECT count(DISTINCT user_id) FROM films_likes')
    logger.info(total_user_id)
    step = total_user_id[0][0] // count
    list_user_id = []
    for offset in range(0, count * step, step):
        user_id = await client.execute(
            f'SELECT user_id FROM films_likes LIMIT 1 OFFSET {offset}'
        )
        list_user_id.append(str(user_id[0][0]))
    logger.debug('Got following list user_id: %s', list_user_id)
    # По полученному списку значений user_id выполняем запросы к базе данных и оцениваем среднее время
    # выполнения запросов
    timer = Timer(name='favorite_films', logger=None)
    counter = 0
    logger.debug('Start iterating on list user_id...')
    for user_id in list_user_id:
        query = f"SELECT film_id FROM films_likes WHERE user_id == '{user_id}'"
        timer.start()
        result = await client.execute(query)
        elapsed_time = timer.stop()
        counter += 1
        logger.debug(
            'Elapsed time [%s] for result query #%s for benchmark_get_list_favorite_films: %s',
            elapsed_time,
            counter,
            result,
        )
    average_time = timer.timers['favorite_films'] / counter
    func_timer.stop()
    total_func_time = func_timer.timers['get_list_favorite_films']
    logger.info(
        """End process measurement of benchmarks get list favorite films.
        Total time: %s sec. Average time: %s sec. Count query: %s.""",
        total_func_time,
        average_time,
        counter,
    )
    return average_time


async def benchmark_get_review_rating(count: int = 100) -> float:
    """Функция оценки среднего времени получения информации о рецензии к фильму,
    включая получения списка лайков и дизлайков рецензии.
    :param count: Количество запросов в базу данных для вычисления среднего значения времени запроса.
    :return: Среднее значение времени выполнения запроса.
    """
    client = aioch.Client(
        host=settings.CH.HOSTS[3],
        port=settings.CH.PORT,
        user=settings.CH.USER,
        password=settings.CH.PASSWORD,
        ca_certs=settings.CH.CACERT,
        secure=True,
    )
    logger.info('Start process measurement of benchmarks get review rating')
    func_timer = Timer('get_review_rating', logger=None)
    func_timer.start()
    list_film_id = await client.execute('SELECT DISTINCT film_id FROM films_reviews')
    logger.debug('Got following list film_id: %s', list_film_id)
    timer = Timer('review_rating', logger=None)
    counter = 0
    logger.debug('Start iterating on list film_id...')
    for film_id, *_ in random.choices(list_film_id, k=count):
        query_review = (
            f'SELECT review_id, film_id, author, text_review, film_review_rating, created_at '
            f"FROM films_reviews WHERE film_id == '{film_id}'"
        )
        timer.start()
        review = await client.execute(query_review)
        likes = await client.execute(
            f"SELECT * FROM review_likes WHERE review_id == '{review[0][0]}'"
        )
        elapsed_time = timer.stop()
        counter += 1
        logger.debug(
            'Elapsed time [%s] for result query #%s for benchmark_get_review_rating:\n"review": %s\n"likes": %s',
            elapsed_time,
            counter,
            review,
            likes,
        )
    average_time = timer.timers['review_rating'] / counter
    func_timer.stop()
    total_func_time = func_timer.timers['get_review_rating']
    logger.info(
        """End process measurement of benchmarks get review rating.
        Total time: %s sec. Average time: %s sec. Count query: %s.""",
        total_func_time,
        average_time,
        counter,
    )
    return average_time


async def count_documents_in_collections():
    client = aioch.Client(
        host=settings.CH.HOSTS[3],
        port=settings.CH.PORT,
        user=settings.CH.USER,
        password=settings.CH.PASSWORD,
        ca_certs=settings.CH.CACERT,
        secure=True,
    )
    reviews_count_documents = await client.execute('SELECT count() FROM films_reviews')
    bookmarks_count_documents = await client.execute('SELECT count() FROM films_bookmarks')
    film_likes_count_documents = await client.execute('SELECT count() FROM films_likes')
    review_likes_count_documents = await client.execute('SELECT count() FROM review_likes')
    return {
        'films_reviews': reviews_count_documents[0][0],
        'films_bookmarks': bookmarks_count_documents[0][0],
        'films_likes': film_likes_count_documents[0][0],
        'review_likes': review_likes_count_documents[0][0],
    }


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    task_get_list_bookmarks = asyncio.ensure_future(
        benchmark_get_list_bookmarks(COUNT_RUN_QUERY)
    )
    task_get_average_rating = asyncio.ensure_future(
        benchmark_get_average_rating(COUNT_RUN_QUERY)
    )
    task_get_list_favorite_film = asyncio.ensure_future(
        benchmark_get_list_favorite_films(COUNT_RUN_QUERY)
    )
    task_get_review_rating = asyncio.ensure_future(
        benchmark_get_review_rating(COUNT_RUN_QUERY)
    )
    task_count_documents = asyncio.ensure_future(count_documents_in_collections())

    benchmark_result_get_list_bookmarks = loop.run_until_complete(task_get_list_bookmarks)
    benchmark_result_get_review_rating = loop.run_until_complete(task_get_review_rating)
    benchmark_result_get_list_favorite_films = loop.run_until_complete(
        task_get_list_favorite_film
    )
    benchmark_result_get_average_rating = loop.run_until_complete(task_get_average_rating)
    count_doc = loop.run_until_complete(task_count_documents)

    total_benchmarks = f"""
## Результаты исследования по измерению скорости чтения и агрегации данных из базы данных Clickhouse\n
### Структура кластера БД
База данных запущена на облачной платформе Yandex.Cloud. Кластер содержит два шарда по две реплики.\n
Топология кластера базы данных:\n
![Топология БД](./images/clickhouse_topology.png)\n
Место, занимаемое таблицами базы данных на диске:
![Место на диске шард 1](./images/clickhouse_database_size_part1.png)
![Место на диске шард 2](./images/clickhouse_database_size_part2.png)
Чтение из всех таблиц базы данных происходит одновременно и асинхронно, имитируя режим чтения из базы данных в
режиме реального времени. Чтение осуществляется отдельными клиентами, подключающимися к разным хостам кластера.\n
### Результаты замеров времени выполнения запросов\n

1. Получение списка понравившихся пользователю фильмов:\n
  - среднее время выполнения запроса: **{benchmark_result_get_list_bookmarks * 1000:.3f}** мс;\n
  - количество записей в таблице `films_bookmarks`: **{count_doc['films_bookmarks']:,d}**;\n
2. Получение информации о рецензии к фильму, включая получения списка лайков и дизлайков рецензии:\n
  - среднее время выполнения запроса: **{benchmark_result_get_review_rating * 1000:.3f} мс**;\n
  - количество записей в таблице `films_reviews`: **{count_doc['films_reviews']:,d}**;\n
  - количество записей в таблице `review_likes`: **{count_doc['review_likes']:,d}**;\n
3. Получение списка понравившихся пользователю фильмов:\n
  - среднее время выполнения запроса: **{benchmark_result_get_list_favorite_films * 1000:.3f} мс**;\n
  - количество записей в таблице `films_likes`: **{count_doc['films_likes']:,d}**;\n
4. Получение средней пользовательской оценки и количества лайков и дизлайков у фильма:\n
  - среднее время выполнения запроса: **{benchmark_result_get_average_rating * 1000:.3f} мс**;\n
  - количество записей в таблице `films_likes`: **{count_doc['films_likes']:,d}**;\n

Результаты замеров времени выполнения запросов к Clickhouse учитывают задержки в сетевом соединении с БД.\n
Оценка величины сетевых задержек:\n
  - сервер Clickhouse_shard1_replica1: `{ping_host(hosts[0])}`\n
  - сервер Clickhouse_shard1_replica2: `{ping_host(hosts[1])}`\n
  - сервер Clickhouse_shard2_replica1: `{ping_host(hosts[2])}`\n
  - сервер Clickhouse_shard2_replica2: `{ping_host(hosts[3])}`\n
"""

    with open('../clickhouse_benchmark.md', 'w', encoding='utf-8') as file:
        print(total_benchmarks, file=file)
