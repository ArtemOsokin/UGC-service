from app.core.config import settings

LOG_DEFAULT_HANDLERS = [
    'default'
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(funcName)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'default': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'fmt': '%(levelprefix)s %(message)s',
            'use_colors': None,
        },
        'access': {
            '()': 'uvicorn.logging.AccessFormatter',
            'fmt': "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",
        },
    },
    'handlers': {
        'console': {
            'level': settings.LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'default': {
            'formatter': 'default',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logconfig.log',
            'maxBytes': 1024,
        },
        'access': {
            'formatter': 'access',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logconfig.log',
            'maxBytes': 1024,
        },
        'services': {
            'formatter': 'verbose',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logconfig.log',
            'maxBytes': 1024,
        },
    },
    'loggers': {
        '': {'handlers': LOG_DEFAULT_HANDLERS, 'level': settings.LOG_LEVEL},
        'uvicorn.error': {'level': 'WARNING'},
        'uvicorn.access': {'handlers': ['access'], 'level': 'INFO', 'propagate': False},
    },
    'root': {
        'level': settings.LOG_LEVEL,
        'formatter': 'verbose',
        'handlers': LOG_DEFAULT_HANDLERS,
    },
}
