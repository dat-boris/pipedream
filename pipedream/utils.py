from functools import wraps
from inspect import isgeneratorfunction

class CacheList():
    def __init__(self, g):
        self.g = g
        self.cache = []

    def pop_cache(self):
        cache = self.cache
        self.cache = []
        return cache

    def generator(self):
        for n in self.g:
            self.cache.append(n)
            yield n


def wrap_function(f, callback):
    """
    A Wrapper function which saves each part into setting

    Parameters
    ----------
    callback: Function
        callback(input, output, func)
    """
    if isgeneratorfunction(f):
        @wraps(f)
        def generator_wrapper(input, **kwargs):
            cache = CacheList(input)
            for o in f(cache.generator()):
                cached_input = cache.pop_cache()
                callback(cached_input, o, f)
                yield o
        return generator_wrapper

    else:
        @wraps(f)
        def func_wrapper(input, **kwargs):
            cache = CacheList(input)
            output = f(cache.generator())
            callback(cache.pop_cache(), output, f)
            return output
        return func_wrapper
