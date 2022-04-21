import datetime
import random
import uuid

from benchmark_db.mongodb.mongodb_benchmark import bookmarks
from benchmark_db.mongodb.mongodb_connect import (conn, film_likes,
                                                  review_likes, reviews)


def gen_film_uuid():
    film_ids = [str(uuid.uuid4()) for _ in range(5000)]
    return film_ids


film_ids = gen_film_uuid()


def gen_user_uuid(count: int = 1000):
    user_ids = (str(uuid.uuid4()) for _ in range(count))
    return user_ids


def write_bookmarks():
    counter = 0
    for user_id in gen_user_uuid(210000):
        count_bookmarks = random.randrange(start=1, stop=51, step=1)
        bookmarks.insert_one(
            {
                "user_id": user_id,
                "bookmarks": [{"film_id": film_id, "created_at": datetime.datetime.utcnow()} for film_id in
                              random.sample(population=film_ids, k=count_bookmarks)]
            }
        )
        counter += 1
        if counter % 1000 == 0:
            print(f'Insert record: {counter}')


def write_film_likes():
    counter = 0
    real_counter = 0
    for user_id in gen_user_uuid(200000):
        count_films = random.randrange(start=1, stop=100, step=1)
        ratings = [round(random.randrange(start=0, stop=100, step=1) / 10, 2) for _ in range(count_films)]
        result = film_likes.insert_many(
            [
                {
                    "user_id": user_id,
                    "film_id": film_id,
                    "user_rating": rating,
                    "is_like": True if rating >= 5 else False,
                    "is_dislike": True if rating < 5 else False,
                    "created_at": datetime.datetime.utcnow()
                }
                for film_id, rating in zip(random.sample(population=film_ids, k=count_films), ratings)
            ]
        )
        counter += 1
        real_counter += len(result.inserted_ids)
        if counter % 1000 == 0:
            print(f'Insert record film likes: {real_counter}')


def write_reviews():
    counter = 0
    real_counter = 0
    idx = 0
    for user_id in gen_user_uuid(10000):
        count_reviews = random.randrange(start=1, stop=100, step=1)
        count_likes = random.randrange(start=1, stop=100, step=1)
        ratings = [random.randrange(start=0, stop=100, step=1) / 10 for _ in range(count_likes)]
        result = reviews.insert_many(
            [
                {
                    "film_id": film_id,
                    "review_id": idx + id_,
                    "text_review": ''.join(random.sample(' qwertyuiopasdfghjklzxcvbnm ', k=random.randrange(1, 15, 1))) * random.randrange(1, 100, 1),
                    "film_review_rating": round(random.randrange(start=0, stop=100, step=1) / 10, 2),
                    "author": user_id,
                    "created_at": datetime.datetime.utcnow()
                }
                for film_id, id_ in zip(random.sample(population=film_ids, k=count_reviews), range(count_reviews))
            ]
        )
        for i in range(count_reviews):
            review_likes.insert_many(
                [
                    {
                        "review_id": idx + i,
                        "user_id": user_id,
                        "is_like": True if rating >= 5 else False,
                        "is_dislike": True if rating < 5 else False,
                        "created_at": datetime.datetime.utcnow()
                    }
                    for rating, user_id in zip(ratings, list(gen_user_uuid(count_likes)))
                ]
            )
        idx += count_reviews
        counter += 1
        real_counter += len(result.inserted_ids)
        if counter % 1000 == 0:
            print(f'Insert record review: {real_counter}')


if __name__ == '__main__':
    write_bookmarks()
    write_film_likes()
    write_reviews()
    conn.close()
