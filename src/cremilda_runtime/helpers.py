from functools import singledispatch

import sidekick as sk
from .types import Err


def safecall(func, *args):
    try:
        return func(*args)
    except Exception as ex:
        return Err(str(ex))


def ismatch(type, value):
    return isinstance(value, type)


@singledispatch
def extract(x):
    return x


@extract.register(sk.Union)
def _(x):
    return x.value if x.args else x
