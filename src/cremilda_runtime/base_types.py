import re

import sidekick as sk
from cremilda.lexer import Lexer

TYPENAME = re.compile(Lexer.TYPENAME)
UnionMeta = type(sk.Union)


def adt(name, **opts):
    """
    Cria um tipo tagged union.

    Args:
        name (str):
            Nome do tipo.
        states (dict):
            Dicionário de {str: bool} que diz para cada estado, se o construtor
            precisa de argumentos ou não.

    Examples:
        >>> adt('Maybe', Just=None, Nothing=object)  # doctest: +ELLIPSIS
        <type Maybe>
    """
    validate_names(name, opts)

    ns = UnionMeta.__prepare__(name, (sk.Union,))
    for opt_name, value in opts.items():
        if value is None:
            ns[opt_name] = sk.opt()
        else:
            ns[opt_name] = sk.opt(value)
    return UnionMeta(name, (sk.Union,), ns)


def validate_names(name, opts):
    if name in opts:
        raise ValueError('type name cannot be one of its states.')
    for name in {name, *opts}:
        if not TYPENAME.fullmatch(name):
            raise ValueError('not a valid type name: %s' % name)
