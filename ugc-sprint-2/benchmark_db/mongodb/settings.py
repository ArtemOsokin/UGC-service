import logging

from pydantic import BaseSettings, Field

logger = logging.getLogger(__name__)


class MongoDBSettings(BaseSettings):
    DB_USER: str = Field('', description='Имя пользователя')
    DB_PASS: str = Field('', description='Пароль пользователя')
    DB_HOSTS: str = Field('', description='Список хостов Mongos')
    DB_NAME: str = Field('', description='Имя базы данных MongoDB')
    CACERT: str = Field('', description='Путь к файлу сертификата SSL')

    class Config:
        env_prefix = 'MONGO_'
        env_file = '.env'


class CommonSettings(BaseSettings):
    LOG_LEVEL: str = Field('INFO', description='Уровень логирования')
    MONGO: MongoDBSettings = MongoDBSettings()


settings = CommonSettings()
