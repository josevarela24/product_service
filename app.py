#!/usr/bin/env python3

import json
import os
import datetime
import logging

import connexion
from connexion import NoContent
from injector import Binder
from flask_injector import FlaskInjector
from connexion.resolver import RestyResolver

from services.redis_service import RedisFactory, RedisIndex


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

logger = logging.getLogger(__name__)

# the socket_timeout parameter is rather important as the default is "no timeout" :-/

def configure(binder: Binder) -> Binder:
    binder.bind(
        RedisIndex,
        RedisIndex(
            RedisFactory(
                REDIS_HOST,
                REDIS_PORT
            )
        )
    )

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    app = connexion.App(__name__, specification_dir='swagger/')
    app.add_api("swagger.yaml", resolver=RestyResolver('api'))
    FlaskInjector(app=app.app, modules=[configure])
    app.run(port=8080)
