import logging
from logging import config as logging_config

import logstash
import sentry_sdk
import uvicorn as uvicorn
from app.api.v1 import ugc_events
from app.core.config import sentry_dsn
from app.core.config import settings
from app.core.logger import LOGGING
from app.core.oauth import decode_jwt
from app.db.kafka_storage import kafka_producer
from app.jaeger_service import init_tracer
from fastapi import Depends, FastAPI, Request
from fastapi.responses import ORJSONResponse
from sentry_sdk.integrations.logging import LoggingIntegration


logging_config.dictConfig(LOGGING)

app = FastAPI(
    title=settings.APP.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    redoc_url='/api/redoc',
    default_response_class=ORJSONResponse,
)

init_tracer(app)
app.logger = logging.getLogger(__name__)
app.logger.setLevel(logging.INFO)
app.logger.addHandler(logstash.LogstashHandler('logstash', 5046, version=1))

sentry_logging = LoggingIntegration(
    level=logging.INFO,  # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
)
sentry_sdk.init(
    sentry_dsn,
    traces_sample_rate=1.0
)


@app.middleware('http')
async def log(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get('X-Request-Id')
    custom_logger = logging.LoggerAdapter(
        app.logger, extra={'tag': 'event', 'request_id': request_id}
    )
    custom_logger.info(request)
    return response


@app.on_event('startup')
async def startup():
    await kafka_producer.instance.start()


@app.on_event('shutdown')
async def shutdown():
    await kafka_producer.instance.stop()


app.include_router(
    ugc_events.router,
    prefix='/api/v1/ugc_events',
    tags=['Пользовательский контент'],
    dependencies=[Depends(decode_jwt)],
)


if __name__ == '__main__':
    uvicorn.run(
        'main:app', host='0.0.0.0', port=8080, log_config=LOGGING, log_level=logging.INFO,
    )
