# -*- coding: utf-8 -*-
# use  Python ver 3.8.5

log_config = {
    'version': 1,
    'formatters': {
        'long_formatter': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
        'short_formatter': {
            'format': '%(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'stderr_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'short_formatter',

        },
        'peewee_file_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'long_formatter',
            'filename': 'peewee.log',
            'encoding': 'UTF-8',

        },
        'peewee_pool_file_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'long_formatter',
            'filename': 'peewee_pool.log',
            'encoding': 'UTF-8',

        },
        'weather_file_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'long_formatter',
            'filename': 'weather.log',
            'encoding': 'UTF-8',

        },
    },
    'loggers': {
        'peewee.pool': {
            'handlers': ['peewee_pool_file_handler'],
            'level': 'DEBUG',
        },
        'peewee': {
            'handlers': ['peewee_file_handler'],
            'level': 'DEBUG',
        },
        'weather': {
            'handlers': ['weather_file_handler'],
            'level': 'DEBUG',
        },

    },
}
