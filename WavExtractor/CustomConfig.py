"""
Copyright 2007
Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
and associated documentation files (the "Software"), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, 
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is 
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or 
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
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
