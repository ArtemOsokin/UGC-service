from typing import Any, Dict, List, Optional
from uuid import UUID

import orjson
from pydantic import BaseModel, Field


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class ORJSONModel(BaseModel):
    def __init__(self, id=None, uuid=None, **kwargs):
        uuid = id or uuid
        super().__init__(uuid=uuid, **kwargs)

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class BaseItemModel(ORJSONModel):
    uuid: UUID = Field(..., title='UUID', description='Уникальный идентификатор')
    name: str = Field(
        ..., title='Имя', description='Полное имя персоны или наименование жанра'
    )


class BaseFilmworkModel(ORJSONModel):
    uuid: UUID = Field(..., title='UUID', description='Уникальный идентификатор фильма')
    title: str = Field(..., title='Заголовок', description='Заголовок фильма или сериала')
    imdb_rating: Optional[float] = Field(
        None, title='Рейтинг', description='Рейтинг фильма по версии IMDb', ge=0, le=10,
    )


class ESSource(ORJSONModel):
    source: Dict[str, Any]

    def __init__(self, _source, **kwargs):
        super().__init__(source=_source, **kwargs)


class ESTotal(ORJSONModel):
    value: int


class ESHits(ORJSONModel):
    hits: List[ESSource]
    total: ESTotal


class ESSearchAnswer(ORJSONModel):
    hits: ESHits
