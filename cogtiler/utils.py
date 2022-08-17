import logging
from decouple import config

def getLogger():
    return logging.getLogger(config('LOGGER', "gunicorn.error"))
