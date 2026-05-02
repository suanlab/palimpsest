from __future__ import annotations

import hashlib
import importlib
import logging
import pickle
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any, ParamSpec, TypeVar, cast

from palimpsest.utils.config import settings

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


class ResponseCache:
    """Persistent response cache backed by diskcache.

    Args:
        directory: Directory for cache files. Defaults to configured cache dir.
    """

    def __init__(self, directory: Path | None = None) -> None:
        self.directory = directory or settings.cache_dir
        self.directory.mkdir(parents=True, exist_ok=True)
        cache_module = importlib.import_module("diskcache")
        self._cache = cache_module.Cache(str(self.directory))

    def get(self, key: str) -> Any | None:
        """Get a cached value.

        Args:
            key: Cache key.

        Returns:
            Cached value if present, otherwise None.
        """

        return self._cache.get(key, default=None)

    def set(self, key: str, value: Any, expire: int = 86400) -> None:
        """Store a value in the cache.

        Args:
            key: Cache key.
            value: Value to cache.
            expire: TTL in seconds.
        """

        self._cache.set(key, value, expire=expire)

    def clear(self) -> None:
        """Clear all cached values.

        Returns:
            None.
        """

        self._cache.clear()

    def __contains__(self, key: str) -> bool:
        """Check whether a key exists in cache.

        Args:
            key: Cache key.

        Returns:
            True if key exists, otherwise False.
        """

        return key in self._cache


def _build_cache_key(
    func: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]
) -> str:
    """Build a stable cache key from a function call.

    Args:
        func: Target function.
        args: Positional arguments.
        kwargs: Keyword arguments.

    Returns:
        Hash-based cache key string.
    """

    payload = {
        "module": func.__module__,
        "qualname": func.__qualname__,
        "args": args,
        "kwargs": tuple(sorted(kwargs.items())),
    }
    try:
        encoded = pickle.dumps(payload, protocol=pickle.HIGHEST_PROTOCOL)
    except (pickle.PickleError, TypeError):
        encoded = repr(payload).encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()
    return f"func:{digest}"


def cached(expire: int = 86400) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Cache function results based on function arguments.

    Args:
        expire: TTL in seconds for each cached call.

    Returns:
        Decorator that caches function return values.
    """

    response_cache = ResponseCache()

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = _build_cache_key(func, args, dict(kwargs))
            cached_value = response_cache.get(key)
            if cached_value is not None:
                return cast(R, cached_value)

            result = func(*args, **kwargs)
            response_cache.set(key, result, expire=expire)
            return result

        return wrapper

    return decorator
