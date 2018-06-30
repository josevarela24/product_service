#!/usr/bin/env python3
from gevent import monkey  # noqa

monkey.patch_all()  # noqa

import json
import os
import redis
import connexion
import datetime
import logging

from connexion import NoContent

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, socket_timeout=5)


def get_redis_key(pet_id):
    return "pets:{}".format(pet_id)


def get_pets(limit, animal_type=None):
    keys = r.keys(get_redis_key("*"))
    return {
        "pets": [_get_pet(key.decode("utf-8").split(":")[1]) for key in keys][:limit]
    }


def _get_pet(pet_id):
    pet = r.get(get_redis_key(pet_id))
    if pet:
        pet = json.loads(pet)
    return pet


def get_pet(pet_id):
    pet = _get_pet(pet_id)
    return pet or connexion.problem(404, "Not found", "Pet not found")


def put_pet(pet_id, pet):
    exists = _get_pet(pet_id)
    pet["id"] = pet_id
    if exists:
        logging.info("Updating pet %s..", pet_id)
        exists.update(pet)
        pet = exists
    else:
        logging.info("Creating pet %s..", pet_id)
        pet["created"] = datetime.datetime.utcnow().isoformat()
    r.set(get_redis_key(pet_id), json.dumps(pet))
    return NoContent, (200 if exists else 201)


def delete_pet(pet_id):
    exists = _get_pet(pet_id)
    if exists:
        logging.info("Deleting pet %s..", pet_id)
        r.delete(get_redis_key(pet_id))
        return NoContent, 204
    else:
        return NoContent, 404


def get_health():
    try:
        r.ping()
    except Exception:
        return connexion.problem(503, "Service Unavailable", "Unhealthy")
    else:
        return "Healthy"


logging.basicConfig(level=logging.INFO)
app = connexion.App(__name__)
app.add_api("swagger.yaml")

if __name__ == "__main__":
    # run our standalone gevent server
    app.run(port=8080, server="gevent")
