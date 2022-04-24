from typing import Optional

from pydantic import BaseSettings, Field


class ClickhouseSettings(BaseSettings):
    USER: Optional[str] = Field(None, description='Имя пользователя')
    PASSWORD: Optional[str] = Field(None, description='Пароль пользователя')
    HOSTS: list[str] = Field(['127.0.0.1', 'localhost'], description='Список имен хостов')
    PORT: int = Field(9440, description='Номер порта clickhouse для соединения с SSL')
    DATABASE: str = Field('', description='Путь к ресурсу источника данных')
    CACERT: str = Field('', description='Путь к файлу сертификата SSL')

    class Config:
        env_prefix = 'CH_'
        env_file = '.env'


class CommonSettings(BaseSettings):
    CH: ClickhouseSettings = ClickhouseSettings()


settings = CommonSettings()
