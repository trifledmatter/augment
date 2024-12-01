from enum import Enum


class RedisErrors(Enum):
    CONNECTION = "redis - could not connect to redis. Is your redis instance running?"
