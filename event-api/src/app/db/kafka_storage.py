import logging
from abc import ABC, abstractmethod
from typing import Optional

from fastapi import Depends
from kafka import KafkaProducer

kafka_producer: Optional[KafkaProducer] = None

logger = logging.getLogger(__name__)


class KafkaStorageError(Exception):
    pass


def get_kafka() -> KafkaProducer:
    return kafka_producer


class AbstractStorage(ABC):
    @abstractmethod
    def send(self, topic, key, value):
        pass


class KafkaStorage(AbstractStorage):
    conn: KafkaProducer

    def __init__(self, kafka_conn: KafkaProducer = Depends(get_kafka)):
        self.conn = kafka_conn

    def send(self, topic, key, value):
        try:
            self.conn.send(topic=topic, key=key, value=value)
        except Exception as send_error:
            logger.error('Error when adding a message to the topic', repr(send_error))
            raise KafkaStorageError from send_error


def get_storage() -> AbstractStorage:
    kafka_producer_ = get_kafka()
    return KafkaStorage(kafka_producer_)









