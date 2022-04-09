import pytest


@pytest.fixture
def v1_bookmarks():
    return 'api/v1/ugc_events/bookmarks'


@pytest.fixture
def v1_feedbacks():
    return 'api/v1/ugc_events/feedbacks'


@pytest.fixture
def v1_():
    return 'api/v1/ugc_events/progress'


@pytest.fixture
def progress_body():
    return {
        "film_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "viewing_progress": 0,
        "viewing_language": "RU",
        "watched": False
    }


@pytest.fixture
def bookmarks_body():
    return {
            "film_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "user_id": "ade835a2-c0e4-4e83-a016-4f26fb319f95",
            "add_to_bookmark": True
            }


@pytest.fixture
def feedbacks_body():
    return {
            "film_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "user_rating": 0,
            "feedback": "string",
            "like_it": False
            }


@pytest.fixture
def auth_token():
    return 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.' \
           'eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY0OTA' \
           'wOTcyNCwianRpIjoiZjk5OGFmYzItZDQxMC0' \
           '0YzBiLThlODUtOGZmNmU4M2I1ZDdiIiwidH' \
           'lwZSI6ImFjY2VzcyIsInN1YiI6ImFkZTgzN' \
           'WEyLWMwZTQtNGU4My1hMDE2LTRmMjZmYjM' \
           'xOWY5NSIsIm5iZiI6MTY0OTAwOTcyNCwiZ' \
           'XhwIjoxNjQ5NjE0NTI0LCJpc19hZG1pbiI' \
           '6ZmFsc2UsImlzX3N0YWZmIjpmYWxz' \
           'ZSwicm9sZXMiOlsiZ3Vlc3QiXX0.' \
           'TCoOawM_1_VitmmCLPhqWLJzm6AbNXQzhQeTW8Bl_pc'


@pytest.fixture
def auth_header(auth_token):
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }
