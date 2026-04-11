import redis
from app.config import settings

pool = redis.ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)
r = redis.Redis(connection_pool=pool)