from abc import ABC
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.models.base import ORJSONModel


class FilmEvents(ABC, ORJSONModel):
    film_id: UUID = Field(
        ...,
        title='Уникальный идентификатор фильма',
        description='Уникальный идентификатор фильма',
    )
    user_id: UUID = Field(
        ...,
        title='Уникальный идентификатор пользователя',
        description='Уникальный идентификатор пользователя',
    )
    _topic: str = Field(
        ..., title='Имя топика', description='Имя топика Kafka для записи события'
    )
    _created_at: datetime = Field(
        datetime.utcnow(), title='Время создания', description='Время создания события'
    )


class FilmBookmark(FilmEvents):
    add_to_bookmark: bool = Field(
        True, title='Добавлено в закладки', description='Статус добавления фильма в закладки'
    )
    _topic = 'films_bookmarks'


class FilmFeedback(FilmEvents):
    user_rating: float = Field(
        ..., title='Пользовательский рейтинг фильма', description='Оценка фильма пользователем'
    )
    feedback: Optional[str] = Field(
        None, title='Отзыв о фильме', description='Отзыв пользователя о фильме'
    )
    like_it: bool = Field(
        False,
        title='Отметка "Нравиться"',
        description='Статус установки отметки "Нравится" пользователем',
    )
    _topic = 'films_feedbacks'


class FilmProgress(FilmEvents):
    viewing_progress: int = Field(
        ...,
        title='Прогресс просмотра',
        description='Прогресс просмотра фильма, секунд с начала',
    )
    viewing_language: str = Field(
        'RU', title='Язык просмотра', description='Язык просмотра фильма'
    )
    watched: bool = Field(
        False, title='Фильм просмотрен', description='Статус завершения просмотра фильма'
    )
    _topic = 'films_progress'
