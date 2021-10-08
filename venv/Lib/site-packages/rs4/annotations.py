import warnings
from functools import wraps

class Uninstalled:
    def __init__ (self, name, libname = None):
        self.name = name
        self.libname = libname or name

    def __call__ (self, *args, **kargs):
        raise ImportError ('cannot import {}, install first (pip install {})'.format (self.name, self.libname))


def deprecated (msg = ""):
    def decorator (f):
        @wraps(f)
        def wrapper (*args, **kwargs):
            nonlocal msg

            warnings.simplefilter ('default')
            warnings.warn (
               "{} will be deprecated{}".format (f.__name__, msg and (", " + msg) or ""),
                DeprecationWarning
            )
            return f (*args, **kwargs)
        return wrapper

    if isinstance (msg, str):
        return decorator
    f, msg = msg, ''
    return decorator (f)

def override (f):
    @wraps (f)
    def wrapper (*args, **karg):
        return f (*args, **karg)
    return wrapper


class _ClassPropertyDescriptor:
    def __init__ (self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__ (self, obj, klass=None):
        if klass is None:
            klass = type (obj)
        return self.fget.__get__ (obj, klass)()

    def __set__ (self, obj, value):
        if not self.fset:
            raise AttributeError ("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__ (obj, type_)(value)

    def setter (self, func):
        if not isinstance (func, (classmethod, staticmethod)):
            func = classmethod (func)
        self.fset = func
        return self

def classproperty (func):
    if not isinstance (func, (classmethod, staticmethod)):
        func = classmethod (func)
    return _ClassPropertyDescriptor (func)

