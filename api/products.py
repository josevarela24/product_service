import json
import logging
import datetime
from flask_injector import inject
from connexion import NoContent

from services.redis_service import RedisIndex

logger = logging.getLogger(__name__)

def get_redis_key(product_id: str) -> str:
    return "products:{}".format(product_id)

@inject
def get_products(indexer: RedisIndex, limit: int, product_type=None):
    # TODO: filter by product_type
    keys = indexer.connection().keys(get_redis_key("*"))
    return {
        "products": [_get_product(indexer, key.decode("utf-8").split(":")[1]) for key in keys][:limit]
    }


def _get_product(indexer: RedisIndex, product_id: str) -> dict:
    """Get product object from Redis"""
    product = indexer.connection().get(get_redis_key(product_id))
    if product:
        product = json.loads(product)
    return product

@inject
def get_product(indexer: RedisIndex, product_id: str):
    product = _get_product(indexer, product_id)
    return product or NoContent, 404

@inject
def put_product(indexer: RedisIndex, product_id: str, product):
    exists = _get_product(indexer, product_id)
    product["id"] = product_id
    if exists:
        logger.info("Updating product %s..", product_id)
        exists.update(product)
        product = exists
    else:
        logger.info("Creating product %s..", product_id)
        product["created"] = datetime.datetime.utcnow().isoformat()
    indexer.connection().set(get_redis_key(product_id), json.dumps(product))
    return NoContent, (200 if exists else 201)

@inject
def delete_product(indexer: RedisIndex, product_id: str):
    exists = _get_product(indexer, product_id)
    if exists:
        logger.info("Deleting product %s..", product_id)
        indexer.connection().delete(get_redis_key(product_id))
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