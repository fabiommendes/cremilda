import pytest

from cremilda import parse
from cremilda.compiler.ast import Atom, Call, Name

flag = pytest.mark.skip


class TestSimpleExpressions:

    def test_can_parse_assignment_of_atomic_types(self):
        check_value('x = 42;', 42)
        check_value('x = 3.14;', 3.14)
        check_value('x = "foo";', "foo")
        check_value('x = true;', True)
        check_value('x = false;', False)

    @flag('branca')
    def test_can_parse_composite_types(self):
        # Depois que implementar suporte, este fica trivial
        check_composite('x = (1, 2);', (1, 2))
        check_composite('x = [1, 2];', (1, 2))
        check_composite('x = {x: 1, y: 2};', dict(x=1, y=2))

    def test_can_parse_function_call(self):
        assert rhs('x = log("hello");') == Call(Name('log'), [Atom('hello')])


def check_value(src, value):
    ast, = parse(src)
    assert isinstance(ast.expr, Atom)
    assert ast.expr.value == value


def check_composite(src, value):
    # TODO!
    ast, = parse(src)
    assert isinstance(ast.expr, Atom)
    assert ast.expr.value == value


def rhs(src):
    ast, = parse(src)
    return ast.expr
