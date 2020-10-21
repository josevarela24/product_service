import json
import logging
import datetime
from flask_injector import inject
from connexion import NoContent

from services.redis_service import RedisIndex

logger = logging.getLogger(__name__)

def get_redis_key(pet_id: str) -> str:
    return "pets:{}".format(pet_id)

@inject
def get_pets(indexer: RedisIndex, limit: int, animal_type=None):
    # TODO: filter by animal_type
    keys = indexer.connection().keys(get_redis_key("*"))
    return {
        "pets": [_get_pet(indexer, key.decode("utf-8").split(":")[1]) for key in keys][:limit]
    }


def _get_pet(indexer: RedisIndex, pet_id: str) -> dict:
    """Get Pet object from Redis"""
    pet = indexer.connection().get(get_redis_key(pet_id))
    if pet:
        pet = json.loads(pet)
    return pet

@inject
def get_pet(indexer: RedisIndex, pet_id: str):
    pet = _get_pet(indexer, pet_id)
    return pet or NoContent, 404

@inject
def put_pet(indexer: RedisIndex, pet_id: str, pet):
    exists = _get_pet(indexer, pet_id)
    pet["id"] = pet_id
    if exists:
        logger.info("Updating pet %s..", pet_id)
        exists.update(pet)
        pet = exists
    else:
        logger.info("Creating pet %s..", pet_id)
        pet["created"] = datetime.datetime.utcnow().isoformat()
    indexer.connection().set(get_redis_key(pet_id), json.dumps(pet))
    return NoContent, (200 if exists else 201)

@inject
def delete_pet(indexer: RedisIndex, pet_id: str):
    exists = _get_pet(indexer, pet_id)
    if exists:
        logger.info("Deleting pet %s..", pet_id)
        indexer.connection().delete(get_redis_key(pet_id))
        return NoContent, 204
    else:
        return NoContent, 404

@inject
def get_health(indexer: RedisIndex):
    try:
        indexer.connection().ping()
    except Exception:
        return NoContent, 503
    else:
        return "Healthy"