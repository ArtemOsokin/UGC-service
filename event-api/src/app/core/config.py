import os

from app.core.dev import DevelopmentSettings
from app.core.prod import ProductionSettings

runtime_settings = os.environ.get('SETTINGS', 'dev')
sentry_dsn = os.environ.get('SENTRY_DSN')

runtime_classes = {
    'dev': DevelopmentSettings,
    'prod': ProductionSettings,
}

if runtime_settings not in runtime_classes:
    expected = ', '.join(runtime_classes)
    raise ValueError(
        f'Wrong SETTINGS environment value! Expected {expected}, got {runtime_settings}.'
    )

settings = runtime_classes[runtime_settings]()
