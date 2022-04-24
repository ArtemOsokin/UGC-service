import logging
from logging import config as logging_config

import uvicorn as uvicorn
from fastapi import Depends, FastAPI
from fastapi.responses import ORJSONResponse

from app.api.v1 import ugc_events
from app.core.config import settings
from app.core.logger import LOGGING
from app.core.oauth import decode_jwt
from app.db.kafka_storage import kafka_producer
from app.jaeger_service import init_tracer

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

print(a)

if __name__ == '__main__':
    uvicorn.run(
        'main:app', host='0.0.0.0', port=8080, log_config=LOGGING, log_level=logging.INFO,
    )
