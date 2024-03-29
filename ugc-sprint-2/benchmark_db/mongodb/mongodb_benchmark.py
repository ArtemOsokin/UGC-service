import asyncio
import logging
import random
from logging import config as logging_config

from benchmark_db.logger import LOGGING_CONFIG
from benchmark_db.mongodb.mongodb_connect import (motor_bookmarks,
                                                  motor_client, motor_db,
                                                  motor_film_likes,
                                                  motor_review_likes,
                                                  motor_reviews)
from benchmark_db.mongodb.settings import settings
from benchmark_db.timer import Timer
from benchmark_db.utils import ping_host

COUNT_RUN_QUERY = 1000  # Количество запросов к базе данных для оценки среднего времени

logging_config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


hosts = list(settings.MONGO.DB_HOSTS.split(','))


async def benchmark_get_list_bookmarks(count: int = 100) -> float:
    """Функция оценки среднего времени получения списка закладок (списка film_id добавленных в закладки фильмов).
    :param count: Количество запросов в базу данных для вычисления среднего значения времени запроса.
    :return: Среднее значение времени выполнения запроса.
    """
    logger.info('Start process measurement of benchmarks get list bookmarks')
    func_timer = Timer('get_list_bookmarks', logger=None)
    func_timer.start()
    # Формируем список user_id в количестве count элементов произвольной выборкой из вспомогательной
    # коллекции, содержащей перечень всех user_id коллекции ugc-movies.bookmarks.
    count_docs = await motor_db.bookmarks_user_ids.count_documents({})
    cursor = motor_db.bookmarks_user_ids.find(
        {}, skip=random.randrange(0, count_docs - count, 1), limit=count
    )
    list_user_id = []
    async for doc in cursor:
        list_user_id.append(doc['_id'])
    logger.debug('Got following list user_id: %s', list_user_id)
    # По полученному списку значений user_id выполняем запросы к базе данных и оцениваем среднее время
    # выполнения запросов
    timer = Timer(name='bookmarks', logger=None)
    counter = 0
    logger.debug('Start iterating on list user_id...')
    for user_id in list_user_id:
        query = {'user_id': user_id}
        timer.start()
        result = await motor_bookmarks.find_one(query, {'bookmarks.film_id': 1, '_id': 0})
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
    logger.info('Start process measurement of benchmarks get average rating movies')
    func_timer = Timer('get_average_rating', logger=None)
    func_timer.start()
    list_film_id = await motor_film_likes.distinct('film_id')
    logger.debug('Got following list film_id: %s', list_film_id)
    timer = Timer('average_rating', logger=None)
    counter = 0
    logger.debug('Start iterating on list film_id...')
    for film_id in random.choices(list_film_id, k=count):
        pipeline = [
            {'$match': {'film_id': film_id}},
            {
                '$group': {
                    '_id': '$film_id',
                    'average_rating': {'$avg': '$user_rating'},
                    'count_likes': {'$sum': {'$toInt': '$is_like'}},
                    'count_dislikes': {'$sum': {'$toInt': '$is_dislike'}},
                    'count_scores': {'$sum': 1},
                }
            },
        ]
        timer.start()
        result = await motor_film_likes.aggregate(pipeline).to_list(None)
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
    logger.info('Start process measurement of benchmarks get list favorite films')
    func_timer = Timer('get_list_favorite_films', logger=None)
    func_timer.start()
    # Формируем список user_id в количестве count элементов произвольной выборкой из вспомогательной
    # коллекции, содержащей перечень всех user_id коллекции ugc-movies.film_likes.
    count_docs = await motor_db.film_likes_user_ids.count_documents({})
    cursor = motor_db.film_likes_user_ids.find(
        {}, skip=random.randrange(0, count_docs - count, 1), limit=count
    )
    list_user_id = []
    async for doc in cursor:
        list_user_id.append(doc['_id'])
    logger.debug('Got following list user_id: %s', list_user_id)
    # По полученному списку значений user_id выполняем запросы к базе данных и оцениваем среднее время
    # выполнения запросов
    timer = Timer(name='favorite_films', logger=None)
    counter = 0
    logger.debug('Start iterating on list user_id...')
    for user_id in list_user_id:
        list_favorite_films = []
        timer.start()
        cursor = motor_film_likes.find(
            {'user_id': user_id, 'is_like': True}, {'film_id': 1, '_id': 0}
        )
        async for doc in cursor:
            list_favorite_films.append(doc['film_id'])
        elapsed_time = timer.stop()
        counter += 1
        logger.debug(
            'Elapsed time [%s] for result query #%s for benchmark_get_list_favorite_films: %s',
            elapsed_time,
            counter,
            list_favorite_films,
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
    logger.info('Start process measurement of benchmarks get review rating')
    func_timer = Timer('get_review_rating', logger=None)
    func_timer.start()
    list_film_id = await motor_reviews.distinct('film_id')
    logger.debug('Got following list film_id: %s', list_film_id)
    timer = Timer('review_rating', logger=None)
    counter = 0
    logger.debug('Start iterating on list film_id...')
    for film_id in random.choices(list_film_id, k=count):
        likes = []
        timer.start()
        review = await motor_reviews.find_one({'film_id': film_id})
        cursor = motor_review_likes.find({'review_id': review['review_id']})
        async for doc in cursor:
            likes.append(doc)
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
    reviews_count_documents = await motor_reviews.count_documents({})
    bookmarks_count_documents = await motor_bookmarks.count_documents({})
    film_likes_count_documents = await motor_film_likes.count_documents({})
    review_likes_count_documents = await motor_review_likes.count_documents({})
    return {
        'reviews': reviews_count_documents,
        'bookmarks': bookmarks_count_documents,
        'film_likes': film_likes_count_documents,
        'review_likes': review_likes_count_documents,
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

    motor_client.close()

    total_benchmarks = f"""
## Результаты исследования по измерению скорости чтения и агрегации данных из базы данных MongoDB\n
### Структура кластера БД
База данных запущена на облачной платформе Yandex.Cloud. Кластер содержит два шарда PRIMARY, без реплицирования.\n
Топология кластера базы данных:\n
![Топология БД](./images/mongodb-topology.png)\n
Перечень и сводная информация по коллекциям базы данных ugc-movies:\n
![Состав коллекций БД](./images/composition_of_collections.png)\n
ER-диаграмма модели коллекций базы данных:\n
![ER-диаграмма](./images/ugc_movies_model_diagram.png)\n
В коллекциях настроено шардирование.\n
Чтение из всех коллекций базы данных происходит одновременно и асинхронно, имитируя режим чтения из базы данных в \
режиме реального времени.\n
### Результаты замеров времени выполнения запросов\n

1. Получение списка понравившихся пользователю фильмов:\n
  - среднее время выполнения запроса: **{benchmark_result_get_list_bookmarks*1000:.3f}** мс;\n
  - количество документов в коллекции `{motor_bookmarks.full_name}`: **{count_doc['bookmarks']:,d}**;\n
2. Получение информации о рецензии к фильму, включая получения списка лайков и дизлайков рецензии:\n
  - среднее время выполнения запроса: **{benchmark_result_get_review_rating*1000:.3f} мс**;\n
  - количество документов в коллекции `{motor_reviews.full_name}`: **{count_doc['reviews']:,d}**;\n
  - количество документов в коллекции `{motor_review_likes.full_name}`: **{count_doc['review_likes']:,d}**;\n
3. Получение списка понравившихся пользователю фильмов:\n
  - среднее время выполнения запроса: **{benchmark_result_get_list_favorite_films*1000:.3f} мс**;\n
  - количество документов в коллекции `{motor_film_likes.full_name}`: **{count_doc['film_likes']:,d}**;\n
4. Получение средней пользовательской оценки и количества лайков и дизлайков у фильма:\n
  - среднее время выполнения запроса: **{benchmark_result_get_average_rating*1000:.3f} мс**;\n
  - количество документов в коллекции `{motor_film_likes.full_name}`: **{count_doc['film_likes']:,d}**;\n

Результаты замеров времени выполнения запросов к MongoDB учитывают задержки в сетевом соединении с БД.\n
Оценка величины сетевых задержек:\n
  - сервер MONGOINFRA#1: `{ping_host(hosts[0])}`\n
  - сервер MONGOINFRA#2: `{ping_host(hosts[1])}`\n
  - сервер MONGOINFRA#3: `{ping_host(hosts[2])}`\n
"""

    with open('../mongodb_benchmark.md', 'w', encoding='utf-8') as file:
        print(total_benchmarks, file=file)
