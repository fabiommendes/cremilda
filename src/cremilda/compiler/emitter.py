import sidekick as sk
from ox.backend import python as py
from ox.backend.python import as_expr, var, let, function, return_
from ox.backend.python.helpers import import_from , lambd
from ox.backend.python.helpers import lambd
from .ast import Expr, Stmt


def to_python(x):
    """
    Converte expressão Cremilda para Python.
    """
    if isinstance(x, Expr):
        return to_python_expr(x)
    elif isinstance(x, Stmt):
        return to_python_stmt(x)
    else:
        raise TypeError('')


@sk.casedispatch.from_namespace(Expr)
class to_python_expr:  # noqa: N801
    """
    Converte expressão Cremilda para Python.
    """

    def Atom(value):  # noqa: N802, N805
        return as_expr(value)

    def Name(value):  # noqa: N802, N805
        return var(value)

    def Call(func, fargs):  # noqa: N802, N805
        args = map(to_python_expr, fargs)
        func = to_python_expr(func)
        return func(*args)

    def Lambda(fargs, expr):
        args = map(var, fargs)
        expr = to_python_expr(expr)
        return lambd(*args)[expr]

    def If(cond, then, other):  # noqa: N802, N805
        cond, then, other = map(to_python_expr, [cond, then, other])
        return py.cond(then, if_=cond, else_=other)

    def else_(expr):  # noqa: N802, N805
        raise NotImplementedError(expr)

    def List(values):
        return as_expr([to_python(x) for x in values])

    def Tuple(values):
        return as_expr(tuple(to_python(x) for x in values))


@sk.casedispatch.from_namespace(Stmt)
class to_python_stmt:  # noqa: N801
    """
    Converte declaração Cremilda para Python.
    """

    def Assign(name, expr):  # noqa: N802, N805
        return let(var(name), to_python_expr(expr))

    def Fundef(name, fargs, expr):  # noqa: N802, N805
        fargs = map(to_python_expr, fargs)
        expr = to_python_expr(expr)
        return function[name](*fargs)[return_(expr)]

    def Import(module, names):
        return import_from(module, names)

    def else_(expr):  # noqa: N802, N805
        raise NotImplementedError(expr)
