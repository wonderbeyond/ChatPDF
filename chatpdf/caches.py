from functools import wraps

from platformdirs import user_cache_dir
from cachelib.file import FileSystemCache

from chatpdf import APP_NAME

cache_dir = user_cache_dir(APP_NAME)

default_cache = FileSystemCache(cache_dir)


def cache_by_args(timeout=5 * 60, prefix="", cache=default_cache):
    """
    Use cases:
    @cache_by_args(3600)
    def f(x, y):
        pass
    from some.package import func
    res = cache_by_args(3600)(func)(x, y)
    """
    cache = cache or default_cache

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            force_update = kwargs.pop("_force_update", False)

            cache_key = "{0}{1}.{2}:{3}".format(
                prefix,
                f.__module__,
                f.__name__,
                ",".join(
                    str(a)
                    for a in list(args)
                    + ["{}={}".format(k, v) for k, v in sorted(kwargs.items())]
                ),
            )

            if not force_update:
                rv = cache.get(cache_key)
                if rv is not None:
                    return rv

            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            return rv

        return decorated_function

    return decorator
