from redis import StrictRedis


class RedisFactory(object):
    def __init__(self, host: str, port:int):
        self.host = host
        self.port = port
    
    def create(self) -> StrictRedis:
        return StrictRedis(host=self.host, port=self.port, db=0, socket_timeout=5)

class RedisIndex(object):
    def __init__( self, redis_factory: RedisFactory ):
        self.redis_factory = redis_factory
        self.instance = None
    
    def connection(self) -> StrictRedis:
        if not self.instance:
            self.instance = self.redis_factory.create()
        
        return self.instance