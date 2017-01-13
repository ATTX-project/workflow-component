import logging
import logging.config


config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'theFormatter': {
            'format': "[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s",
            'datefmt': '%Y-%m-%d %H:%M:%S %z',
            'class': 'logging.Formatter'
        },
        'access': {
            'format': '%(message)s',
            'class': 'logging.Formatter'
        }
    },
    'handlers': {
        'fileHandler': {
            'level': 'INFO',
            'formatter': 'theFormatter',
            'class': 'logging.FileHandler',
            'filename': 'logs/api.log',
            'mode': 'a+'
        },
        'consoleHandler': {
            'level': 'INFO',
            'formatter': 'theFormatter',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout'
        }
    },
    'loggers': {
        '': {
            'handlers': ['consoleHandler'],
            'level': 'INFO',
            'propagate': True
        },
        'mainLogger': {
            'handlers': ['consoleHandler', 'fileHandler'],
            'level': 'INFO',
            'propagate': True
        },
        'appLogger': {
            'handlers': ['consoleHandler', 'fileHandler'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

logging.config.dictConfig(config)
app_logger = logging.getLogger('appLogger')
main_logger = logging.getLogger('mainLogger')