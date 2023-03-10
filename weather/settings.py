# This settings file is the same as settings_base.py but enables logging.

from weather.settings_base import *

if not os.path.exists('logs'):
    os.mkdir('logs')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'timestamp_and_level': {
            'format':
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"module": "%(name)s", "line": "%(lineno)d", '
            '"data": %(message)s}',
            'style':
            '%',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'timestamp_and_level',
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'timestamp_and_level',
            'filename': 'logs/log.info.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
