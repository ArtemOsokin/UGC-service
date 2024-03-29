import datetime
import logging
import random
import uuid
from logging import config as logging_config

from benchmark_db.logger import LOGGING_CONFIG
from benchmark_db.mongodb.mongodb_connect import (motor_bookmarks,
                                                  motor_client,
                                                  motor_film_likes,
                                                  motor_review_likes,
                                                  motor_reviews)

logging_config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def gen_film_uuid():
    film_ids = [str(uuid.uuid4()) for _ in range(5000)]
    return film_ids


film_ids = gen_film_uuid()


def gen_user_uuid(count: int = 1000):
    user_ids = (str(uuid.uuid4()) for _ in range(count))
    return user_ids


async def write_bookmarks():
    counter = 0
    for user_id in gen_user_uuid(210000):
        count_bookmarks = random.randrange(start=1, stop=51, step=1)
        await motor_bookmarks.insert_one(
            {
                'user_id': user_id,
                'bookmarks': [
                    {'film_id': film_id, 'created_at': datetime.datetime.utcnow()}
                    for film_id in random.sample(population=film_ids, k=count_bookmarks)
                ],
            }
        )
        counter += 1
        if counter % 1000 == 0:
            logger.info('Insert bookmarks for %s users.', counter)


async def write_film_likes():
    counter = 0
    real_counter = 0
    for user_id in gen_user_uuid(200000):
        count_films = random.randrange(start=1, stop=100, step=1)
        ratings = [
            round(random.randrange(start=0, stop=100, step=1) / 10, 2)
            for _ in range(count_films)
        ]
        result = await motor_film_likes.insert_many(
            [
                {
                    'user_id': user_id,
                    'film_id': film_id,
                    'user_rating': rating,
                    'is_like': True if rating >= 5 else False,
                    'is_dislike': True if rating < 5 else False,
                    'created_at': datetime.datetime.utcnow(),
                }
                for film_id, rating in zip(
                    random.sample(population=film_ids, k=count_films), ratings
                )
            ]
        )
        counter += 1
        real_counter += len(result.inserted_ids)
        if counter % 1000 == 0:
            logger.info(
                'Movie likes inserted for %s users. Total record: %s', counter, real_counter
            )


async def write_reviews():
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
        result = await motor_reviews.insert_many(
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
                    'created_at': datetime.datetime.utcnow(),
                }
                for film_id, id_ in zip(
                    random.sample(population=film_ids, k=count_reviews), range(count_reviews)
                )
            ]
        )
        real_rows_review += len(result.inserted_ids)
        for i in range(count_reviews):
            result = await motor_review_likes.insert_many(
                [
                    {
                        'review_id': idx + i,
                        'user_id': user_id,
                        'is_like': True if rating >= 5 else False,
                        'is_dislike': True if rating < 5 else False,
                        'created_at': datetime.datetime.utcnow(),
                    }
                    for rating, user_id in zip(ratings, list(gen_user_uuid(count_likes)))
                ]
            )
            real_rows_likes += len(result.inserted_ids)
        idx += count_reviews
        counter += 1
        if counter % 1000 == 0:
            logger.info(
                'Review inserted for %s movies. Inserted %s likes of reviews.',
                real_rows_review,
                real_rows_likes,
            )


async def gen_user_id_collection_from_bookmarks():
    pipeline = [
        {'$group': {'_id': '$user_id'}},
        {'$sort': {'_id': 1}},
        {'$out': 'bookmarks_user_ids'},
    ]
    async for _ in motor_bookmarks.aggregate(pipeline, allowDiskUse=True):
        pass


async def gen_user_id_collection_from_film_likes():
    pipeline = [
        {'$sort': {'film_id': 1}},
        {'$group': {'_id': '$user_id'}},
        {'$out': 'film_likes_user_ids'},
    ]
    async for _ in motor_film_likes.aggregate(pipeline, allowDiskUse=True):
        pass


if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()
    task_write_bookmarks = asyncio.ensure_future(write_bookmarks())
    task_write_film_likes = asyncio.ensure_future(write_film_likes())
    task_write_reviews = asyncio.ensure_future(write_reviews())

    loop.run_until_complete(
        asyncio.wait([task_write_reviews, task_write_film_likes, task_write_reviews])
    )
    if task_write_bookmarks.done():
        loop.run_until_complete(gen_user_id_collection_from_bookmarks())

    if task_write_film_likes.done():
        loop.run_until_complete(gen_user_id_collection_from_film_likes())

    motor_client.close()
