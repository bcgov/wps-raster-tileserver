""" Central location to instantiate redis for easier mocking in unit tests.
"""
from redis import StrictRedis
from decouple import config


def _create_redis():
    return StrictRedis(host=config('REDIS_HOST', ),
                       port=config('REDIS_PORT', 6379),
                       db=0,
                       password=config('REDIS_PASSWORD'))


def create_redis():
    """ Call _create_redis, to make it easy to mock out for everyone in unit testing. """
    return _create_redis()
