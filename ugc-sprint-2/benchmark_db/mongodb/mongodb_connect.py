from urllib.parse import quote_plus as quote

import pymongo
from settings import settings

url = 'mongodb://{user}:{pw}@{hosts}/?authSource={auth_src}'.format(
    user=quote(settings.MONGO.DB_USER),
    pw=quote(settings.MONGO.DB_PASS),
    hosts=settings.MONGO.DB_HOSTS,
    auth_src=settings.MONGO.DB_NAME
)

conn = pymongo.MongoClient(url, tlsCAFile=settings.MONGO.CACERT)

db = conn[settings.MONGO.DB_NAME]
bookmarks = db.bookmarks
film_likes = db.film_likes
reviews = db.reviews
review_likes = db.review_likes
