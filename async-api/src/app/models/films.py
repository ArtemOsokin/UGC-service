from typing import List

from pydantic import Field

from app.models.base import BaseFilmworkModel, BaseItemModel, ORJSONModel


class ESFilmwork(BaseFilmworkModel):
    """Schema describe Filmwork instance doc,
    which will get from ElasticSearch"""

    description: str = Field(
        None, title='Содержание фильма', description='Краткое содержание фильма'
    )
    genre: List[BaseItemModel] = Field(list(), title='Жанр', description='Жанр фильма')
    actors: List[BaseItemModel] = Field(list(), title='Актёры', description='Список актёров')
    writers: List[BaseItemModel] = Field(
        list(), title='Сценаристы', description='Список сценаристов'
    )
    directors: List[BaseItemModel] = Field(
        list(), title='Режисёры', description='Список режисёров'
    )
    actors_name: List[str] = Field(
        list(), title='Имена актёров', description='Список имён актёров'
    )
    writers_name: List[str] = Field(
        list(), title='Имена сценаристов', description='Список имён сценаристов'
    )
    directors_name: List[str] = Field(
        list(), title='Имена режисёров', description='Список имён режисёров'
    )


class ESListFilmworks(ORJSONModel):
    """Schema describe list Filmwork instance doc,
    which will get from ElasticSearch"""

    items: List[ESFilmwork]
