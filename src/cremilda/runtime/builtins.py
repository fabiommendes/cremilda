"""
Funções builtins estão disponíveis publicamente como funções Cremilda.
"""
import operator as __op

from . import helpers as __helpers
from .base import Operator as _operator, Assoc as __assoc  # noqa: N813
from .types import (
    Float, Bool, String, Tuple, Record,
    Maybe, Just, Nothing,
    Result, Ok, Err,
    List, Cons, Nil
)

# ==============================================================================
# Helpers
# ==============================================================================

# Funções que estão disponíveis sempre, mas são consideradas privadas de uso
# do compilador. Elas auxiliam a geração de código e não devem ser utilizadas
# diretamente em código cremilda
__safecall = __helpers.safecall
__ismatch = __helpers.ismatch
__iscase = __helpers.iscase
__extract_value_from_case = __helpers.extract_value_from_case
__multimethod = __helpers.multimethod
__typed_arg = __helpers.typed_arg
__left_op = (lambda prec, op, func: _operator(op, func, __assoc.LEFT, prec))
__right_op = (lambda prec, op, func: _operator(op, func, __assoc.RIGHT, prec))
__default_types = (
    Float, Bool, String, Tuple, Record,
    Maybe, Just, Nothing,
    Result, Ok, Err,
    List, Cons, Nil
)
__default_operators = {}

# ==============================================================================
# Funções da inteface pública
# ==============================================================================

# Multimétodos -----------------------------------------------------------------
count = __multimethod('count')
index = __multimethod('index')
index_end = __multimethod('index_end')

# Conversões -------------------------------------------------------------------
to_number = float
to_string = str
show = repr

# Strings ----------------------------------------------------------------------

# Maiúsculas/minúsculas
capitalize = str.capitalize
casefold = str.casefold
lowercase = str.lower
swapcase = str.swapcase
titlecase = str.title
uppercase = str.upper

# Centralização
center = str.center
left_justify = str.ljust
right_justify = str.rjust

# Transformações
strip = str.strip
strip_start = str.lstrip
strip_end = str.rstrip
expand_tabs = str.expandtabs
replace = str.replace
zero_fill = str.zfill

# Localizando elementos
count.register(str, str.count)
find = str.find
find_end = str.rfind
index.register(str)(str.index)
index_end.register(str)(str.rindex)

# Testando propriedades
is_alphanumeric = str.isalnum
is_alphabetic = str.isalpha
is_decimal = str.isdecimal
is_digit = str.isdigit
is_identifier = str.isidentifier
is_lowercase = str.islower
is_numeric = str.isnumeric
is_printable = str.isprintable
is_space = str.isspace
is_titlecase = str.istitle
is_uppercase = str.isupper
ends_with = str.endswith
starts_with = str.startswith

# Divisão em substrings
partition = str.partition
partition_end = str.rpartition
split_end = str.rsplit
split = str.split
split_lines = str.splitlines

# Juntando lista de strings
join = str.join

# Tuplas e listas --------------------------------------------------------------
first = __helpers.typed_arg((tuple, list), lambda x: empty(x) and x[0])
last = __helpers.typed_arg((tuple, list), lambda x: empty(x) and x[-1])


def empty(x):
    if isinstance(x, str):
        return ''
    elif isinstance(x, list):
        return []
    elif isinstance(x, tuple):
        return ()
    else:
        return Err(f'{x.__class__.__name__} cannot be empty')


@__helpers.typed_arg((tuple, list))
def trest(x):
    n = len(x)
    if n == 0:
        return x
    elif n == 2:
        return x[1]
    else:
        return x[1:]


# Debug ------------------------------------------------------------------------
def log(obj):
    """
    Imprime valor no terminal e retorna argumento.
    """
    print(obj)
    return obj


def debug(name, value):
    """
    Imprime valor no terminal e retorna argumento.
    """
    print('%s = %r' % (name, value))
    return value


# ==============================================================================
# Funções associadas a operadores
# ==============================================================================

# generaliza operatores para testes em python
opp = lambda op: (lambda a, b: op(float(a), float(b)))

# Aritiméticas
add = opp(float.__add__)
mul = opp(float.__mul__)
sub = opp(float.__sub__)
div = opp(float.__truediv__)
mod = opp(float.__mod__)
pow = opp(float.__pow__)

# Comparações
equal = __op.eq
not_equal = __op.ne
ge = __op.ge
le = __op.le
gt = __op.gt
lt = __op.lt

# Sequências e strings
cons = (lambda x, xs: [x, *xs])


def concat(x, y):
    if x.__class__ is y.__class__ and isinstance(x, (list, str)):
        return x + y
    else:
        xtype = x.__class__.__name__
        ytype = y.__class__.__name__
        return Err(f'cannot concatenate {xtype} and {ytype}')


# Operadores unários
neg = (lambda x: -x)
pos = (lambda x: +x)
negate = (lambda x: not x)

# Operadores de funções
pipe = (lambda x, f: f(x))  # y |> f
reverse_pipe = (lambda f, x: f(x))  # f <| x
compose = (lambda f, g: lambda *args: g(f(*args)))  # f >> g
reverse_compose = (lambda f, g: lambda *args: f(g(*args)))  # f << g

# Registra operadores binários
__default_operators.update({
    # Aplicação de funções
    '|>': __left_op(1, '|>', pipe),
    '<|': __right_op(1, '<|', reverse_pipe),

    # Listas e sequências
    '::': __left_op(2, '::', cons),
    '++': __left_op(3, '++', concat),

    # Operações booleanas
    'or': __left_op(4, '::', cons),
    'and': __left_op(5, '++', concat),

    # Comparações
    '==': __left_op(6, '==', equal),
    '!=': __left_op(6, '!=', not_equal),
    # 'is': __left_op(6, 'is', identical), ?
    # 'is not': __left_op(6, 'is not', not_identical), ?
    '<': __left_op(7, '<', lt),
    '>': __left_op(7, '>', gt),
    '<=': __left_op(7, '<=', le),
    '>=': __left_op(7, '>=', ge),
    # 'in': __left_op(7, 'in', is_contained), ?
    # 'not in': __left_op(7, 'not in', is_not_contained), ?

    # Aritimeticos
    '+': __left_op(8, '+', add),
    '-': __left_op(8, '-', sub),
    '*': __left_op(9, '*', mul),
    '/': __left_op(9, '/', div),
    '%': __left_op(9, '%', mod),
    '**': __left_op(10, '**', pow),

    # Composição de funções
    '>>': __left_op(11, '<<', compose),
    '<<': __right_op(11, '>>', reverse_compose),
})

# ==============================================================================
# Escolhe nomes exportados
# ==============================================================================
__all__ = [
    x for x in globals()
    if not x.startswith('_') or x.startswith('__') and not x.endswith('__')
]
