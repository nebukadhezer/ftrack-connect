# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack
import os
from logging import NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
from logging import getLogger as _getLogger
from logging import getLevelName, basicConfig, captureWarnings
from logging import config as _config
import logging as _logging
import appdirs

user_data_dir = appdirs.user_data_dir('ftrack-connect', 'ftrack')
log_directory = os.path.join(user_data_dir, 'log')
if not os.path.exists(log_directory):
    os.makedirs(log_directory)


logfile = os.path.join(log_directory, 'ftrack.log')

DEFAULT_HANDLERS = ['console', 'file']

DEFAULT_LOG_SETTINGS = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'WARNING',
            'formatter': 'file',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'file',
            'filename': logfile,
            'mode': 'a',
            'maxBytes': 10485760,
            'backupCount': 5,
        },

    },
    'formatters': {
        'file': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': DEFAULT_HANDLERS,
        },
        'ftrack_api': {
            'level': 'INFO',
        },
        'FTrackCore': {
            'level': 'INFO',
        }
    }
}

_config.dictConfig(DEFAULT_LOG_SETTINGS)
captureWarnings(True)


def getLogger(name=None):
    return _getLogger(name)
