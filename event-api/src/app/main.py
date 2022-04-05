import logging
import os
from logging import config as logging_config

import backoff
import uvicorn as uvicorn
from app.api.v1 import ugc_events
from app.core.backoff_handler import backoff_hdlr, backoff_hdlr_success
from app.core.config import settings
from app.core.logger import LOGGING
from app.core.oauth import decode_jwt
from app.db import kafka_storage
from app.jaeger_service import init_tracer
from fastapi import Depends, FastAPI
from fastapi.responses import ORJSONResponse
from kafka import KafkaProducer

logging_config.dictConfig(LOGGING)

app = FastAPI(
    title=settings.APP.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    redoc_url='/api/redoc',
    default_response_class=ORJSONResponse,
)

init_tracer(app)


@app.on_event('startup')
async def startup():
    if not settings.KAFKA.RUN_IN_YANDEX_CLOUD:
        kafka_storage.kafka_producer = backoff.on_exception(
            wait_gen=backoff.expo,
            max_tries=settings.BACKOFF.RETRIES,
            max_time=settings.BACKOFF.MAX_TIME,
            exception=Exception,
            on_backoff=backoff_hdlr,
            on_success=backoff_hdlr_success,
        )(KafkaProducer)(
            bootstrap_servers=[f'{settings.KAFKA.HOST}:{settings.KAFKA.PORT}'],
            compression_type='gzip',
        )
    else:
        kafka_storage.kafka_producer = backoff.on_exception(
            wait_gen=backoff.expo,
            max_tries=settings.BACKOFF.RETRIES,
            max_time=settings.BACKOFF.MAX_TIME,
            exception=Exception,
            on_backoff=backoff_hdlr,
            on_success=backoff_hdlr_success,
        )(KafkaProducer)(
            bootstrap_servers=[f'{settings.KAFKA.HOST_YC}:{settings.KAFKA.PORT_YC}'],
            security_protocol=settings.KAFKA.SECURITY_PROTOCOL,
            sasl_mechanism=settings.KAFKA.SASL_MECHANISM,
            sasl_plain_password=settings.KAFKA.PRODUCER_PASSWORD,
            sasl_plain_username=settings.KAFKA.PRODUCER_USERNAME,
            ssl_cafile=settings.KAFKA.PATH_CERTIFICATE,
        )


@app.on_event('shutdown')
async def shutdown():
    kafka_storage.kafka_producer.close()


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
