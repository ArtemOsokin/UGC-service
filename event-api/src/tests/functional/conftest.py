import asyncio
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import aiohttp
import orjson
import pytest
import uvicorn
from functional.settings import (SERVICE_URL, TEST_SRC_DIR_PATH,
                                 test_settings)
from httpx import AsyncClient
from jose import jwt
from kafka import KafkaConsumer
from multidict import CIMultiDictProxy

from app.core.config import settings
from app.core.logger import LOGGING
from app.main import app

assert test_settings.TESTING, 'You must set TESTING=True env for run the tests.'


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope='session', autouse=True)
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def load_fixture():
    def load(filename):
        with open(Path(TEST_SRC_DIR_PATH) / filename, encoding='utf-8') as file:
            return orjson.loads(file.read())

    return load


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_post_request(make_post_request_aiohttp, make_post_request_httpx):
    """Возвращаем разные функции формирования запроса get в зависимости от значения env RUN_WITH_COVERAGE:
     True:  Hа базе клиента AsyncClient пакета httpx для корректной оценки охвата кода тестами.
                В этом случае используется приложение, запущенное локально в рамках тестовой сессии
                на тестовом сервере UvicornTestServer.
     False: На базе клиента aiohttp.ClientSession если оценка охвата кода тестами не требуется.
                В этом случае запросы get адресуются к серверу uvicorn в контейнере приложения"""

    return (
        make_post_request_httpx if test_settings.RUN_WITH_COVERAGE else make_post_request_aiohttp
    )


@pytest.fixture
def make_post_request_aiohttp(session):
    async def inner(
        endpoint_url: str, params: Optional[dict] = None, headers: Optional[dict] = None
    ) -> HTTPResponse:
        params = params or {}
        headers = headers or {}
        url = urljoin(base=SERVICE_URL, url=endpoint_url)
        async with session.post(url, params=params, headers=headers) as response:
            return HTTPResponse(
                body=(
                    await response.json()
                    if response.headers['Content-Type'] == 'application/json'
                    else await response.text()
                ),
                headers=response.headers,
                status=response.status,
            )

    return inner


@pytest.fixture
def make_post_request_httpx(app_server):
    async def inner(
        endpoint_url: str, params: Optional[dict] = None, headers: Optional[dict] = None
    ) -> HTTPResponse:
        params = params or {}
        headers = headers or {}
        url = urljoin(base=SERVICE_URL, url=endpoint_url)
        async with AsyncClient(app=app, base_url=SERVICE_URL, follow_redirects=True) as ac:
            response = await ac.post(url=url, params=params, headers=headers)
            return HTTPResponse(
                body=(
                    response.json()
                    if response.headers['Content-Type'] == 'application/json'
                    else response.text()
                ),
                headers=response.headers,
                status=response.status_code,
            )

    return inner


@pytest.fixture(scope='function')
def expected(load_fixture, request):
    return load_fixture(request.param)


@pytest.fixture(scope='function')
def expected_not_found(load_fixture):
    return load_fixture('not_found_response.json')


class UvicornTestServer(uvicorn.Server):
    """Uvicorn test server

    Usage:
        @pytest.fixture
        server = UvicornTestServer()
        await server.up()
        yield server
        await server.down()
    """

    def __init__(self, application, host='127.0.0.1', port=8888):
        """Create a Uvicorn test server

        Args:
            application (FastAPI, optional): the FastAPI app. Defaults to main.app.
            host (str, optional): the host ip. Defaults to '127.0.0.1'.
            port (int, optional): the port. Defaults to PORT.
        """
        self._serve_task = None
        self._startup_done = asyncio.Event()
        super().__init__(
            config=uvicorn.Config(
                application, host=host, port=port, log_config=LOGGING, log_level=logging.INFO,
            )
        )

    async def startup(self, sockets: Optional[list] = None) -> None:
        """Override uvicorn startup"""
        await super().startup(sockets=sockets)
        self.config.setup_event_loop()
        self._startup_done.set()

    async def up(self) -> None:
        """Start up server asynchronously"""
        self._serve_task = asyncio.create_task(self.serve())
        await self._startup_done.wait()

    async def down(self) -> None:
        """Shut down server asynchronously"""
        self.should_exit = True
        await self._serve_task


@pytest.fixture(scope='session')
async def app_server():
    """Start server as test fixture and tear down after test"""
    server = UvicornTestServer(app)
    await server.up()
    yield server
    await server.down()


@pytest.fixture(autouse=True)
def subscriber_headers():
    payload = {'is_admin': True, 'is_staff': False, 'roles': ['subscriber']}
    token = jwt.encode(payload, settings.AUTH.SECRET_KEY, algorithm=settings.AUTH.ALGORITHM)
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(autouse=True)
def consumer_bookmarks():
    consumer = KafkaConsumer(
        'films_bookmarks',
        bootstrap_servers=['broker:9092'],
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id='echo-messages-to-stdout',
    )
    return consumer


@pytest.fixture(autouse=True)
def consumer_feedbacks():
    consumer = KafkaConsumer(
        'films_feedbacks',
        bootstrap_servers=['broker:9092'],
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id='echo-messages-to-stdout',
    )
    return consumer


@pytest.fixture(autouse=True)
def consumer_progress():
    consumer = KafkaConsumer(
        'films_progress',
        bootstrap_servers=['broker:9092'],
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id='echo-messages-to-stdout',
    )
    return consumer
