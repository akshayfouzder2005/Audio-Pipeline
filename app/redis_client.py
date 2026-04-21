import redis
from app.config import settings

pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    ssl_cert_reqs=None
)
r = redis.Redis(connection_pool=pool)