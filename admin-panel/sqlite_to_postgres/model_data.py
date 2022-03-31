import uuid
from datetime import datetime, date
from dataclasses import dataclass


@dataclass
class Person:
    __slots__ = ('id', 'full_name', 'birth_date', 'created_at', 'updated_at')
    id: uuid.UUID
    full_name: str
    birth_date: date
    created_at: datetime
    updated_at: datetime


@dataclass
class FilmWork:
    __slots__ = (
        'id', 'title', 'description', 'creation_date', 'certificate',
        'file_path', 'rating', 'type', 'created_at', 'updated_at'
    )
    id: uuid.UUID
    title: str
    description: str
    creation_date: date
    certificate: str
    file_path: str
    rating: float
    type: str
    created_at: datetime
    updated_at: datetime


@dataclass
class GenreFilmWork:
    __slots__ = ('id', 'film_work_id', 'genre_id', 'created_at')
    id: uuid.UUID
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created_at: datetime


@dataclass
class PersonFilmWork:
    __slots__ = ('id', 'film_work_id', 'person_id', 'role', 'created_at')
    id: uuid.UUID
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    created_at: datetime


@dataclass(frozen=True)
class Genre:
    __slots__ = ('id', 'name', 'description', 'created_at', 'updated_at')
    id: uuid.UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
