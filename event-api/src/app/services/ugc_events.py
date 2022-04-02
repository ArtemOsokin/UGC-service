from abc import ABC, abstractmethod
from functools import lru_cache
from logging import getLogger

import orjson
from app.db.kafka_storage import AbstractStorage, get_storage
from app.models.ugc_events import FilmEvents
from fastapi import Depends

logger = getLogger(__name__)


class AbstractService(ABC):
    name = None

    def __init__(self, storage: AbstractStorage):
        self.storage = storage

    @abstractmethod
    def post(self, *args):
        pass


class FilmUGCService(AbstractService):
    def __init__(self, *args, **kwargs):
        self.name = 'film_ugc_events'
        super().__init__(*args, **kwargs)

    def post(self, message: FilmEvents):
        logger.info(message.json())
        key = f'{message.user_id}_{message.film_id}'
        event_message = orjson.dumps(message.dict())
        event_topic = message.topic
        result = self.storage.send(event_topic, key.encode(), event_message)
        if result:
            logger.info(f'Записано сообщение {event_message} в топик {event_topic}')


@lru_cache()
def get_film_ugc_service(storage: AbstractStorage = Depends(get_storage),) -> FilmUGCService:
    return FilmUGCService(storage)
