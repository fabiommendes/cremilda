import pytest

import sidekick as sk
from cremilda.compiler import compile_source, compile_to_module
from cremilda_runtime.types import Just, Nothing

HELLO_MODULE = """
def _module():
    from cremilda_runtime import log
    msg = log('hello world!')
    return {}
globals().update(_module())
"""


class TestCompilationToPythonSource:
    def test_can_emit_correct_hello_word_module(self):
        src = 'msg = log("hello world!");'
        assert compile_source(src) == HELLO_MODULE.strip()


class TestCompilationToPythonModule:
    def get_main(self, src):
        return getattr(self.get_mod(src), '__main', None)

    def get_mod(self, src):
        return compile_to_module(src, 'testmod')

    def test_initialize_atomic_variables(self):
        assert self.get_main('main = "hello";') == 'hello'

    # Estruturas de dados e valores
    @pytest.mark.skip('red')
    def test_support_for_lists(self):
        assert self.get_main('main = [1, 2, 3];') == [1, 2, 3]
        assert self.get_main('main = [1, 2, add(1, 2)];') == [1, 2, 3]

    @pytest.mark.skip()
    def test_support_for_records(self):
        assert self.get_main('main = {foo = "bar"};') == {'foo': 'bar'}
        assert self.get_main('main = {foo = add(1, 2)};') == {'foo': 3}

    @pytest.mark.skip()
    def test_support_for_attribute_access(self):
        assert self.get_main('x = {foo = "bar"}; main = x.foo;') == 'bar'
        assert self.get_main('main = {foo = "bar"}.foo;') == 'bar'

    @pytest.mark.skip()
    def test_support_for_tag_constructor(self):
        assert self.get_main('main = Just 42;') == Just(42)
        assert self.get_main('main = Nothing;') == Nothing

    @pytest.mark.skip()
    def test_support_for_lambdas(self):
        func = self.get_main('main = x => add(x, x);')
        assert func(1) == 2 and func(2) == 4

        func = self.get_main('main = (x, y) => add(x, y);')
        assert func(1, 2) == 3 and func(2, 3) == 5

    # Controle de fluxo
    @pytest.mark.skip()
    def test_support_for_let_expressions(self):
        assert self.get_main('main = let x=40; y=2; in x + y;') == 42
        assert self.get_main(
            'main = '
            '   let \n'
            '       x = 40;\n'
            '       y = 2;\n'
            '   in x + y;') == 42

    @pytest.mark.skip()
    def test_grammar_converts_function_defs_in_lambdas(self):
        assert self.get_main(
            'main = '
            '   let \n'
            '       f(x) = 2 * x;\n'
            '       y = 21;\n'
            '   in f(y);') == 42

    @pytest.mark.skip()
    def test_support_for_case_expressions(self):
        assert self.get_main(
            'main = '
            '   case Just 42 of'
            '       Just x => x;'
            '       Nothing => 0;') == 42

    @pytest.mark.skip()
    def test_else_clause_in_case_expressions(self):
        assert self.get_main(
            'main = '
            '   case Just 42 of'
            '       Just x => x;'
            '       else => 0;') == 42

    # Operadores
    @pytest.mark.skip()
    def test_support_for_unary_operators(self):
        assert self.get_main('main = -2;') == -2
        assert self.get_main('main = +2;') == +2
        assert self.get_main('main = not true;') == False

    @pytest.mark.skip()
    def test_support_for_arbitrary_binary_operators(self):
        # Mais difícil que parece! Primeiro deve determinar a precedência e
        # associatividade de cada operador. Depois, deve trocar a expressão
        # com operadores pelo seu correspondente como chamada de função.
        assert self.get_main('main = 40 + 2;') == 42
        assert self.get_main('main = "foo" ++ "bar";') == 'foobar'

    @pytest.mark.skip()
    def test_support_new_operator_definition(self):
        mod = self.get_mod('infixl 9 (.+) => add;')
        op = getattr(mod, '__operators')['.+']
        assert op.symbol == '.+'
        assert op.precedence == 9
        assert op.associativity == 'left'

        mod = self.get_mod('infixr 9 (.+) => add;')
        op = getattr(mod, '__operators')['.+']
        assert op.symbol == '.+'
        assert op.precedence == 9
        assert op.associativity == 'right'

    @pytest.mark.skip()
    def test_replaces_binary_operator_by_function_application(self):
        assert self.get_main('infixl 9 (.+) => add; main = 40 .+ 2;') == 42

    # Namespaces
    @pytest.mark.skip()
    def test_support_for_declaring_export_variables(self):
        assert self.get_mod('export (foo); foo = 42;').foo == 42
        mod = self.get_mod('export (foo, bar); foo = 40; bar = 2;')
        assert mod.foo == 40
        assert mod.bar == 2

    @pytest.mark.skip()
    def test_support_for_import_all(self):
        assert self.get_main('import "math"; main = sqrt(4);') == 2

    @pytest.mark.skip()
    def test_support_for_qualified_import(self):
        assert self.get_main('import "math" as math; main = math.sqrt(4);') == 2

    @pytest.mark.skip()
    def test_support_for_import_names(self):
        assert self.get_main('import "math" exposing (sqrt); main = sqrt(4);') == 2

    # Typedefs
    @pytest.mark.skip()
    def test_support_type_definition_with_generic_type(self):
        value = self.get_main('type Option = Value a | Nil; '
                              'main = Value 42')
        assert str(value) == 'Value(42.0)'
        assert isinstance(value, sk.Union)

    @pytest.mark.skip()
    def test_support_type_definition(self):
        value = self.get_main('type Option = Value Number | Nil;'
                              'main = Value 42')
        assert str(value) == 'Value(42.0)'
        assert isinstance(value, sk.Union)

        Value = type(value)
        with pytest.raises(ValueError):
            Value("foo")

    @pytest.mark.skip()
    def test_exporting_type_also_exports_its_sub_types(self):
        mod = self.get_mod(
            'export (Option);'
            'type Option = Value x'
            '            | Nil; '
            'main = Value 42'
        )
        assert issubclass(mod.Option, sk.Union)
        assert issubclass(mod.Value, mod.Option)
        assert issubclass(mod.Nil, mod.Option)
        assert mod.Value != mod.Option
        assert mod.Nil != mod.Option
