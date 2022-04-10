import json

import pytest
from starlette import status

pytestmark = pytest.mark.asyncio


async def test_films_bookmarks(
        make_post_request,
        v1_bookmarks,
        bookmarks_body,
        auth_token,
        auth_header,
        consumer_bookmarks
):
    mes = next(consumer_bookmarks).value
    response = await make_post_request(v1_bookmarks,
                                       headers=json.dumps(auth_header(auth_token)),
                                       body=json.dumps(bookmarks_body)
                                       )
    assert response.status == status.HTTP_202_ACCEPTED
    assert mes == bookmarks_body


async def test_films_feedbacks(
        make_post_request,
        v1_feedbacks,
        feedbacks_body,
        auth_token,
        auth_header,
        consumer_feedbacks
):
    mes = next(consumer_feedbacks).value
    response = await make_post_request(v1_feedbacks,
                                       headers=json.dumps(auth_header(auth_token)),
                                       body=json.dumps(feedbacks_body)
                                       )
    assert response.status == status.HTTP_202_ACCEPTED
    assert mes == feedbacks_body


async def test_films_progress(
        make_post_request,
        v1_progress,
        progress_body,
        auth_token,
        auth_header,
        consumer_progress
):
    mes = next(consumer_progress).value
    response = await make_post_request(v1_progress,
                                       headers=json.dumps(auth_header(auth_token)),
                                       body=json.dumps(progress_body)
                                       )
    assert response.status == status.HTTP_202_ACCEPTED
    assert mes == progress_body
