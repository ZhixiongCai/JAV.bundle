# coding=utf-8

def with_default(default):
    def wrapper(func):
        def wrap(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return default
        return wrap
    return wrapper
