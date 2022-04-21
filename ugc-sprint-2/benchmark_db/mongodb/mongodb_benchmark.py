from timeit import timeit

from benchmark_db.mongodb.mongodb_connect import (bookmarks, conn, film_likes,
                                                  review_likes, reviews)
from benchmark_db.mongodb.settings import settings
from pythonping import ping


def ping_host(host):
    ping_result = ping(target=host, count=100, timeout=2)

    return {
        'host': host,
        'avg_latency': ping_result.rtt_avg_ms,
        'min_latency': ping_result.rtt_min_ms,
        'max_latency': ping_result.rtt_max_ms,
        'packet_loss': ping_result.packet_loss
    }


hosts = list(settings.MONGO.DB_HOSTS.split(','))


def get_list_bookmarks():
    """Функция получения списка закладок (списка film_id добавленных в закладки фильмов)"""
    result = bookmarks.find({'user_id': '7e282f42-2c0e-4b67-835c-db3684bfbca1'}, {'bookmarks.film_id': 1, '_id': 0})
    return [item.get('film_id') for item in result[0].get('bookmarks')]


def get_average_rating():
    """Функция получения средней пользовательской оценки и количества лайков и дизлайков у фильма"""
    result = film_likes.aggregate(
        [
            {'$match': {'film_id': '9c4cb53c-e42b-4807-8039-40a831b34b90'}},
            {
                '$group':
                    {
                        '_id': '$film_id',
                        'average_rating': {'$avg': '$user_rating'},
                        'count_likes': {'$sum': {'$toInt': '$is_like'}},
                        'count_dislikes': {'$sum': {'$toInt': '$is_dislike'}},
                        'count_scores': {'$sum': 1}
                    }
            }
        ]
    )
    return list(result)


def get_list_favorite_films():
    """Функция получения списка понравившихся пользователю фильмов"""
    result = film_likes.find_one({'user_id': 'c7fc9738-05f1-48d6-9724-21eeb2d251c8', 'is_like': True},
                                 {'film_id': 1, '_id': 0})
    return list(item for item in result)


def get_review_rating():
    """Функция получения информации о рецензии к фильму, включая получения списка лайков и дизлайков рецензии"""
    review = reviews.find_one(
        {'film_id': '0c3717ac-81f4-48f3-9c6c-a7858cc8abb1', 'author': 'c938c8b8-2965-4ea6-a383-efbabf45967c'})
    likes = list(item for item in review_likes.find({'review_id': review['review_id']}))
    return review, likes


reviews_count_documents = reviews.count_documents({})
bookmarks_count_documents = bookmarks.count_documents({})
film_likes_count_documents = film_likes.count_documents({})
review_likes_count_documents = review_likes.count_documents({})

benchmark_result_get_review_rating = timeit('get_review_rating()', 'from __main__ import get_review_rating',
                                            number=1000)
benchmark_result_get_list_bookmarks = timeit('get_list_bookmarks()', 'from __main__ import get_list_bookmarks',
                                             number=1000)
benchmark_result_get_average_rating = timeit('get_average_rating()', 'from __main__ import get_average_rating',
                                             number=1000)
benchmark_result_get_list_favorite_films = timeit('get_list_favorite_films()',
                                                  'from __main__ import get_list_favorite_films', number=1000)

total_benchmark = f"""
## Результаты исследования по измерению скорости чтения и агрегации данных из базы данных MongoDB\n
### Структура кластера БД
База данных запущена на облачной платформе Yandex.Cloud.
Кластер содержит два шарда PRIMARY, без реплицирования.\n
Топология базы данных:\n
![Топология БД](./mongodb-topology.png)\n
Перечень и сводная информация по коллекциям базы данных ugc-movies:\n
![Состав коллекций БД](./composition_of_collections.png)\n
В коллекциях настроено шардирование.\n
### Результаты замеров времени выполнения запросов

1. Получение списка понравившихся пользователю фильмов:\n
  - среднее время выполнения запроса: **{benchmark_result_get_list_bookmarks:.3f}** мс;\n
  - количество документов в коллекции `{bookmarks.full_name}`: **{bookmarks_count_documents:,d}**;\n
2. Получение информации о рецензии к фильму, включая получения списка лайков и дизлайков рецензии:\n
  - среднее время выполнения запроса: **{benchmark_result_get_review_rating:.3f} мс**;\n
  - количество документов в коллекции `{reviews.full_name}`: **{reviews_count_documents:,d}**;\n
  - количество документов в коллекции `{review_likes.full_name}`: **{review_likes_count_documents:,d}**;\n
3. Получение списка понравившихся пользователю фильмов:\n
  - среднее время выполнения запроса: **{benchmark_result_get_list_favorite_films:.3f} мс**;\n
  - количество документов в коллекции `{film_likes.full_name}`: **{film_likes_count_documents:,d}**;\n
4. Получение средней пользовательской оценки и количества лайков и дизлайков у фильма:\n
  - среднее время выполнения запроса: **{benchmark_result_get_average_rating:.3f} мс**;\n
  - количество документов в коллекции `{film_likes.full_name}`: **{film_likes_count_documents:,d}**;\n

Результаты замеров времени выполнения запросов к MongoDB учитывают задержки в сетевом соединении с БД.\n
Оценка величины сетевых задержек:\n
  - сервер MONGOINFRA#1: `{ping_host(hosts[0])}`\n
  - сервер MONGOINFRA#2: `{ping_host(hosts[1])}`\n
  - сервер MONGOINFRA#3: `{ping_host(hosts[2])}`\n
"""

with open('../mongodb_benchmark.md', 'w', encoding='utf-8') as file:
    print(total_benchmark, file=file)

conn.close()
