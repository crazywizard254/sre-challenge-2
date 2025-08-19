import os
import uuid
from typing import Set, Optional


def _get_redis():
    import redis
    url = os.getenv('REDIS_URL', os.getenv('REDIS', 'redis://redis:6379/0'))
    return redis.from_url(url)


def new_wishlist_id() -> str:
    return uuid.uuid4().hex


def add_favorite(wishlist_id: str, part_id: int) -> bool:
    r = _get_redis()
    key = f"wishlist:{wishlist_id}"
    return r.sadd(key, int(part_id)) == 1


def remove_favorite(wishlist_id: str, part_id: int) -> bool:
    r = _get_redis()
    key = f"wishlist:{wishlist_id}"
    return r.srem(key, int(part_id)) == 1


def list_favorites(wishlist_id: str) -> Set[int]:
    r = _get_redis()
    key = f"wishlist:{wishlist_id}"
    vals = r.smembers(key) or set()
    return set(int(x) for x in vals)


def is_favorite(wishlist_id: str, part_id: int) -> bool:
    r = _get_redis()
    key = f"wishlist:{wishlist_id}"
    return r.sismember(key, int(part_id))
