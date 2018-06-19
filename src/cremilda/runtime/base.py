import enum
import re
import typing

import sidekick as sk

TYPENAME = re.compile(r'[A-Z][a-zA-Z0-9_]*')
UnionMeta = type(sk.Union)


class Assoc(enum.Enum):
    LEFT = 'left'
    RIGHT = 'right'


class Operator(sk.Record):
    """
    Representa um operator em runtime.
    """

    SYMBOL_MAP = {
        '-': 'sub',
        '+': 'plus',
        '*': 'mul',
        '/': 'div',
        '<': 'lt',
        '>': 'gt',
        '?': 'Q',
        '@': 'at',
        '&': 'and',
        '$': 'S',
        '^': 'hat',
        '~': 'td',
        '%': 'pc',
        '=': 'eq',
        ':': '__',
    }

    symbol: str = sk.field(str)
    function: str = sk.field(str)
    assoc: Assoc = sk.field(Assoc)
    precedence: int = sk.field(int)

    def export_name(self):
        to_ascii = self.SYMBOL_MAP
        return '__op_' + ''.join(to_ascii[x] for x in self.symbol)


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
