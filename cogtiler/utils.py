import logging
from decouple import config
from redis import StrictRedis


def getLogger():
    return logging.getLogger(config('LOGGER', "gunicorn.error"))



def _create_redis():
    return StrictRedis(host=config('REDIS_HOST', ),
                       port=config('REDIS_PORT', 6379),
                       db=0,
                       password=config('REDIS_PASSWORD'))


def create_redis():
    """ Call _create_redis, to make it easy to mock out for everyone in unit testing. """
    return _create_redis()