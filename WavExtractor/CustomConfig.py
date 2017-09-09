from functools import wraps

class CustomConfigDecorators(object):

    @staticmethod
    def getter(func):
        @wraps(func)
        def func_wrapper(self):
            if hasattr(self, '_' + func.__name__):
                return getattr(self, '_' + func.__name__)
            return func(self)
        return func_wrapper

    @staticmethod
    def setter(func):
        @wraps(func)
        def func_wrapper(self, value):
            return setattr(self, '_' + func.__name__, func(self, value))
        return func_wrapper
