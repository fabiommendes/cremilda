from cremilda import parse
from cremilda.emitter import to_python

from ox.backend.python import let, var


class TestEmmitToPythonStmt:
    def rhs(self, src):
        return parse(src).expr

    def check_equiv(self, src, python):
        ast, = parse(src)
        py_ast = to_python(ast)
        py_src = py_ast.source()
        if py_src != python:
            assert compile(py_src, '<input>', 'exec') \
                   == compile(python, '<input>', 'exec')

    def expr(self, src):
        return self.rhs('x = %s;' % src)

    def test_can_emit_correct_hello_word_expression(self):
        ast, = parse('msg = log("hello world!");')
        assert to_python(ast) == let(msg=var.log('hello world!'))

    def test_convert_variable_assignment(self):
        self.check_equiv('x = 42;',
                         'x = 42.0')

    def test_convert_function_calls(self):
        self.check_equiv('x = f(y, "foo");',
                         'x = f(y, "foo")')
