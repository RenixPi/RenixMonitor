import logging

loggers = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'generic_format': {'format': '%(name)s : %(levelname)s %(message)s', 'datefmt': '%Y-%m-%d %H:%M:%S'},
    },
    'handlers': {
        'ecu_handler': {
            'class': 'logging.StreamHandler',
            'level': logging.INFO,
            'formatter': 'generic_format',
            'stream': 'ext://sys.stdout'
        },
        'null_handler': {
            'class': 'logging.NullHandler'
        }
    },
    'loggers': {
        'ecu': {
            'level': logging.INFO,
            'handlers': ['ecu_handler']
        },
    }
}

