from functools import wraps

class CustomConfigDecorators(object):
    """
    Decorators for custom configuration to handle book-keeping of custom values.
    """

    @staticmethod
    def getter(func):
        """Decorator to allow getters to read _attr for a given attr"""
        @wraps(func)
        def func_wrapper(self):
            if hasattr(self, '_' + func.__name__):
                return getattr(self, '_' + func.__name__)
            return func(self)
        return func_wrapper

    @staticmethod
    def setter(func):
        """
        Decorator to allow setters to write a custom value _attr for a given attr.
        Decorated function should return the value to write, or raise an exception 
        if the value is invalid.
        """
        @wraps(func)
        def func_wrapper(self, value):
            return setattr(self, '_' + func.__name__, func(self, value))
        return func_wrapper
