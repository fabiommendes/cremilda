"""
Funções builtins estão disponíveis publicamente como funções Cremilda.
"""
import operator as _op

#
# Operações básicas
# ------------------------------------------------------------------------------

# Aritimeticas
add = float.__add__
mul = float.__mul__
sub = float.__sub__
div = float.__truediv__
pow = float.__pow__
neg = float.__neg__

# Comparações
equal = _op.eq
not_equal = _op.ne
ge = _op.ge
le = _op.le
gt = _op.gt
lt = _op.lt

# Sequencias e strings
concat = str.__add__

#
# Funções built-ins
# ------------------------------------------------------------------------------

# Conversões
parse_number = float
to_string = str
show = repr


# Debug
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
