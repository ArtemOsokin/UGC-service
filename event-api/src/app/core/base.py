import logging

from pydantic import BaseSettings, Field

logger = logging.getLogger(__name__)


class APPSettings(BaseSettings):
    PROJECT_NAME: str = Field('UGS-service', description='Имя проекта')

    class Config:
        env_prefix = 'APP_'
        env_file = '.env'


class TracingSettings(BaseSettings):
    AGENT_HOST_NAME: str = Field('127.0.0.1', description='адрес хоста агента Jaeger')
    AGENT_PORT: int = Field(6831, description='номер порта агента Jaeger')
    ENABLED: bool = Field(False, description='Флаг влк./откл. трассировки')

    class Config:
        env_prefix = 'JAEGER_'


class AuthSettings(BaseSettings):
    SECRET_KEY: str = Field('super_big_secret', description='Секретный ключ JWT')
    ALGORITHM: str = Field('HS256', description='Алгоритм шифрования')

    class Config:
        env_prefix = 'AUTH_'


class KafkaSettings(BaseSettings):
    HOST: str = Field('127.0.0.1', description='Адрес хоста брокера Kafka')
    PORT: int = Field(9092, description='Номер порта брокера Kafka')
    RUN_IN_YANDEX_CLOUD: bool = Field(False, description='KAFKA запущена на кластере Яндекс.Облако')
    HOST_YC: str = Field('127.0.0.1', description='FQDN хоста-брокера')
    PORT_YC: int = Field(9091, description='Номер порта брокера Kafka')
    PRODUCER_PASSWORD: str = Field('password', description='Пароль для роли Producer на хосте-брокере KAFKA в Яндекс.Облако')
    PRODUCER_USERNAME: str = Field('kafka_producer', description='Имя роли Producer на хосте-брокере KAFKA в Яндекс.Облако')
    SECURITY_PROTOCOL: str = Field('SASL_SSL', description='Тип протокола безопасности')
    SASL_MECHANISM: str = Field('SCRAM-SHA-512', description='Механизм безопасности')
    PATH_CERTIFICATE: str = Field('', description='Путь к SSL сертификату')
    PRODUCER_TIMEOUT_MS: int = Field(3000, description='Таймаут запроса KafkaProducer')
    CLIENT_ID: str = Field('aiokafka-producer-film_ugc_events', description='Имя клиента Kafka-Producer')

    class Config:
        env_prefix = 'KAFKA_'


class BackoffSettings(BaseSettings):
    RETRIES: int = Field(
        5, description='количество повторных попыток подключения к внешним сервисам'
    )
    TTS: int = Field(2, description='Время ожидания до следующей попытки в секундах')
    MAX_TIME: int = Field(120, description='Максимальное время ожидания для попытки')

    class Config:
        env_prefix = 'BACKOFF_'
        env_file = '.env'
        

class CommonSettings(BaseSettings):
    LOG_LEVEL: str = Field('INFO', description='Уровень логирования сервисов приложения')
    APP: APPSettings = APPSettings()
    JAEGER: TracingSettings = TracingSettings()
    AUTH: AuthSettings = AuthSettings()
    KAFKA: KafkaSettings = KafkaSettings()
    BACKOFF: BackoffSettings = BackoffSettings()
