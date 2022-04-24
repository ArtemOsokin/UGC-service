from urllib.parse import quote_plus as quote

from motor.motor_asyncio import AsyncIOMotorClient
from settings import settings

url = 'mongodb://{user}:{pw}@{hosts}/?authSource={auth_src}'.format(
    user=quote(settings.MONGO.DB_USER),
    pw=quote(settings.MONGO.DB_PASS),
    hosts=settings.MONGO.DB_HOSTS,
    auth_src=settings.MONGO.DB_NAME,
)

motor_client = AsyncIOMotorClient(url, tlsCAFile=settings.MONGO.CACERT)
motor_db = motor_client[settings.MONGO.DB_NAME]
motor_bookmarks = motor_db.bookmarks
motor_film_likes = motor_db.film_likes
motor_reviews = motor_db.reviews
motor_review_likes = motor_db.review_likes
