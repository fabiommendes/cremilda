from cremilda import parse
from cremilda.compiler.ast import Atom, Call, Name


class TestSimpleExpressions:
    def check_assign(self, src, value):
        ast, = parse(src)
        assert isinstance(ast.expr, Atom)
        assert ast.expr.value == value

    def rhs(self, src):
        ast, = parse(src)
        return ast.expr

    def test_can_parse_assignment_of_atomic_types(self):
        checker = self.check_assign
        checker('x = 42;', 42)
        checker('x = 3.14;', 3.14)
        checker('x = "foo";', "foo")
        checker('x = true;', True)
        checker('x = false;', False)

    def test_can_parse_composite_types(self):
        checker = self.check_assign
        # checker('x = (1, 2);', (1, 2))
        # checker('x = [1, 2];', (1, 2))
        # checker('x = {x=1, y=2};', record(x=1, y=2))

    def test_can_parse_function_call(self):
        rhs = self.rhs
        assert rhs('x = log("hello");') == Call(Name('log'), [Atom('hello')])
