import logging
import random
import uuid
from datetime import datetime
from logging import config as logging_config

import aioch
from benchmark_db.clickhouse.settings import settings
from benchmark_db.logger import LOGGING_CONFIG

logging_config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def gen_film_uuid():
    film_ids = [str(uuid.uuid4()) for _ in range(5000)]
    return film_ids


film_ids = gen_film_uuid()


def gen_user_uuid(count: int = 1000):
    user_ids = (str(uuid.uuid4()) for _ in range(count))
    return user_ids


async def insert_bookmarks():
    client = aioch.Client(
        host=settings.CH.HOSTS[0],
        port=settings.CH.PORT,
        user=settings.CH.USER,
        password=settings.CH.PASSWORD,
        ca_certs=settings.CH.CACERT,
        secure=True,
    )
    counter = 0
    real_rows = 0
    for user_id in gen_user_uuid(210000):
        count_bookmarks = random.randrange(start=1, stop=51, step=1)
        row_count_bookmarks = await client.execute(
            'INSERT INTO films_bookmarks (user_id, film_id, created_at) VALUES',
            [
                {'user_id': user_id, 'film_id': film_id, 'created_at': datetime.utcnow()}
                for film_id in random.sample(population=film_ids, k=count_bookmarks)
            ],
        )
        counter += 1
        real_rows += row_count_bookmarks
        if counter % 1000 == 0:
            logger.info('Insert bookmarks for %s users. Total record: %s', counter, real_rows)


async def insert_film_likes():
    client = aioch.Client(
        host=settings.CH.HOSTS[1],
        port=settings.CH.PORT,
        user=settings.CH.USER,
        password=settings.CH.PASSWORD,
        ca_certs=settings.CH.CACERT,
        secure=True,
    )
    counter = 0
    real_rows = 0
    for user_id in gen_user_uuid(200000):
        count_films = random.randrange(start=1, stop=100, step=1)
        ratings = [
            round(random.randrange(start=0, stop=100, step=1) / 10, 2)
            for _ in range(count_films)
        ]
        rv = await client.execute(
            'INSERT INTO films_likes (user_id, film_id, user_rating, is_like, is_dislike, created_at) VALUES',
            [
                {
                    'user_id': user_id,
                    'film_id': film_id,
                    'user_rating': rating,
                    'is_like': 1 if rating >= 5 else 0,
                    'is_dislike': 1 if rating < 5 else 0,
                    'created_at': datetime.utcnow(),
                }
                for film_id, rating in zip(
                    random.sample(population=film_ids, k=count_films), ratings
                )
            ],
        )
        counter += 1
        real_rows += rv
        if counter % 1000 == 0:
            logger.info(
                'Movie likes inserted for %s users. Total record: %s', counter, real_rows
            )


async def insert_reviews():
    client = aioch.Client(
        host=settings.CH.HOSTS[2],
        port=settings.CH.PORT,
        user=settings.CH.USER,
        password=settings.CH.PASSWORD,
        ca_certs=settings.CH.CACERT,
        secure=True,
    )
    counter = 0
    real_rows_review = 0
    real_rows_likes = 0
    idx = 0
    for user_id in gen_user_uuid(10000):
        count_reviews = random.randrange(start=1, stop=100, step=1)
        count_likes = random.randrange(start=1, stop=100, step=1)
        ratings = [
            random.randrange(start=0, stop=100, step=1) / 10 for _ in range(count_likes)
        ]
        row_count_review = await client.execute(
            'INSERT INTO films_reviews (film_id, review_id, text_review, film_review_rating, author, created_at) VALUES',
            [
                {
                    'film_id': film_id,
                    'review_id': idx + id_,
                    'text_review': ''.join(
                        random.sample(
                            ' qwertyuiopasdfghjklzxcvbnm ', k=random.randrange(1, 15, 1)
                        )
                    ) * random.randrange(1, 100, 1),
                    'film_review_rating': round(
                        random.randrange(start=0, stop=100, step=1) / 10, 2
                    ),
                    'author': user_id,
                    'created_at': datetime.utcnow(),
                }
                for film_id, id_ in zip(
                    random.sample(population=film_ids, k=count_reviews), range(count_reviews)
                )
            ],
        )
        real_rows_review += row_count_review
        for i in range(count_reviews):
            row_count_likes = await client.execute(
                'INSERT INTO review_likes (review_id, user_id, is_like, is_dislike, created_at) VALUES',
                [
                    {
                        'review_id': idx + i,
                        'user_id': user_id,
                        'is_like': 1 if rating >= 5 else 0,
                        'is_dislike': 1 if rating < 5 else 0,
                        'created_at': datetime.utcnow(),
                    }
                    for rating, user_id in zip(ratings, list(gen_user_uuid(count_likes)))
                ],
            )
            real_rows_likes += row_count_likes
        idx += count_reviews
        counter += 1
        if counter % 1000 == 0:
            logger.info(
                'Review inserted for %s movies. Inserted %s likes of reviews.',
                real_rows_review,
                real_rows_likes,
            )


if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.wait([insert_bookmarks(), insert_reviews(), insert_film_likes()])
    )
