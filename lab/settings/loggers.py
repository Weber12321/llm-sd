import functools
import logging


def log_io(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(
            "Calling %s with args: %s, kwargs: %s", 
            func.__name__, args, kwargs
        )
        result = func(*args, **kwargs)
        logging.info("%s returned %s", func.__name__, result)
        return result
    return wrapper