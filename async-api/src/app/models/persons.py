from typing import List
from uuid import UUID

from pydantic import Field

from app.models.base import BaseFilmworkModel, ORJSONModel


class ESPerson(ORJSONModel):
    """Schema describe Person instance doc,
    which will get from persons index ElasticSearch"""

    uuid: UUID = Field(title='UUID', description='Уникальный идентификатор')
    full_name: str = Field(
        title='Имя персоны', description='Полное имя актера, сценариста или режисёра'
    )
    roles: List[str] = Field(
        title='Роль', description='Роль в фильме: актёр, сценарист или режисёр'
    )
    film_ids: List[UUID] = Field(
        title='Фильмы', description='Перечень фильмов, в которых принимал участие'
    )


class ESFilmworkPerson(BaseFilmworkModel):
    """Schema describe Film instance doc by person,
    which will get from movies index ElasticSearch"""


class ESListPersons(ORJSONModel):
    """Schema describe list Person instance doc,
    which will get from persons index ElasticSearch"""

    items: List[ESPerson]


class ESListFilmPersonSchema(ORJSONModel):
    """Schema describe list Film instance doc by person,
    which will get from movies index ElasticSearch"""

    items: List[ESFilmworkPerson]
