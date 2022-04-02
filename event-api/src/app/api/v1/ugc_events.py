from logging import getLogger
from uuid import UUID

from app.core.oauth import get_user_id
from app.db.kafka_storage import KafkaStorageError
from app.models.ugc_events import FilmBookmark, FilmFeedback, FilmProgress
from app.services.ugc_events import FilmUGCService, get_film_ugc_service
from fastapi import APIRouter, Depends, HTTPException
from starlette import status

logger = getLogger(__name__)

router = APIRouter()


@router.post(
    '/bookmarks',
    tags=['ugc'],
    summary='События добавления фильма в закладки',
    description='Фиксация события по добавлению пользователем фильма в закладки',
    operation_id='addFilmBookmark',
)
def bookmark_add(
    bookmark: FilmBookmark,
    film_ugc_service: FilmUGCService = Depends(get_film_ugc_service),
    user_id: UUID = Depends(get_user_id),
):
    bookmark.user_id = user_id
    try:
        film_ugc_service.post(bookmark)
        return status.HTTP_202_ACCEPTED
    except KafkaStorageError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Storage not available',
        )


@router.post(
    '/feedbacks',
    tags=['ugc'],
    summary='События оценки фильма пользователем',
    description='Фиксация событий оценки пользователем фильма - лайки, отзывы, пользовательский рейтинг фильма',
    operation_id='addFilmFeedback',
)
def feedback_add(
    feedback: FilmFeedback,
    film_ugc_service: FilmUGCService = Depends(get_film_ugc_service),
    user_id: UUID = Depends(get_user_id),
):
    feedback.user_id = user_id
    try:
        film_ugc_service.post(feedback)
        return status.HTTP_202_ACCEPTED
    except KafkaStorageError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Storage not available',
        )


@router.post(
    '/progress',
    tags=['ugc'],
    summary='События прогресса просмотра фильма',
    description='Фиксация прогресса просмотра фильма и языка просмотра',
    operation_id='addFilmProgress',
)
def progress_add(
    progress: FilmProgress,
    film_ugc_service: FilmUGCService = Depends(get_film_ugc_service),
    user_id: UUID = Depends(get_user_id),
):
    progress.user_id = user_id
    try:
        film_ugc_service.post(progress)
        return status.HTTP_202_ACCEPTED
    except KafkaStorageError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Storage not available',
        )
