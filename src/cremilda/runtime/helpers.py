from functools import singledispatch, wraps

import sidekick as sk
from .types import Err


def safecall(func, *args):
    try:
        return func(*args)
    except Exception as ex:
        return Err(str(ex))


def ismatch(type, value):
    return isinstance(value, type)


def iscase(type, value):
    return type is value or isinstance(value, type)


@singledispatch
def extract_value_from_case(x):
    return x


@extract_value_from_case.register(sk.Union)
def _(x):
    return x.value if x.args else x


def typed_arg(cls, func=None):
    if func is None:
        return lambda func: typed_arg(cls, func)

    msg = f'{func.__name__} expect {type.__name__} arguments.'

    @wraps(func)
    def wrapped(x):
        if isinstance(x, cls):
            return func(x)
        else:
            return Err(msg)

    return wrapped


def multimethod(name):
    msg = f'{name} does not accept %s arguments'

    @singledispatch
    def function(x):
        return Err(msg % x.__class__.__name__)

    return function
