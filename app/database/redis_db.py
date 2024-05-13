import redis
import json
from datetime import datetime
from app.config import REDIS_HOST, REDIS_PORT, REDIS_DB

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def json_serializer(data):
    """Custom JSON serializer to handle complex data types like datetime."""
    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return super(CustomEncoder, self).default(obj)
    return json.dumps(data, cls=CustomEncoder)

def cache_data(key, data, expire=10):
    """
    Cache any data with serialization and an expiration time.
    """
    serialized_data = json_serializer(data)
    redis_client.setex(key, expire, serialized_data)

def get_cached_data(key):
    """
    Retrieve and deserialize any cached data.
    """
    data = redis_client.get(key)
    return json.loads(data) if data else None

def delete_cached_data(key):
    """
    Delete any cached data from Redis.
    """
    redis_client.delete(key)

def cache_event(event_id, event_data):
    """
    Specifically cache event data using an event-specific key.
    """
    key = f"event:{event_id}"
    cache_data(key, event_data, expire=10)  

def get_cached_event(event_id):
    """
    Retrieve cached event data using an event-specific key.
    """
    key = f"event:{event_id}"
    return get_cached_data(key)

def delete_cached_event(event_id):
    """
    Delete cached event data using an event-specific key.
    """
    key = f"event:{event_id}"
    delete_cached_data(key)
