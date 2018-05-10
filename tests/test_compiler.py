import pytest

import sidekick as sk
from cremilda.compiler import transpile, compile_module
from cremilda.compiler.ast import Assoc
from cremilda.runtime import Just, Nothing
from cremilda.runtime.base import Operator

flag = pytest.mark.skip

HELLO_MODULE = """
def _module():
    from cremilda.runtime import log
    msg = log('hello world!')
    return {}
globals().update(_module())
"""


class TestCompilationToPythonSource:
    def test_can_emit_correct_hello_word_module(self):
        src = 'msg = log("hello world!");'
        assert transpile(src) == HELLO_MODULE.strip()


class TestCompilationToPythonModule:
    def get_main(self, src):
        return getattr(self.get_mod(src), '__main', None)

    def get_mod(self, src):
        return compile_module(src, 'testmod')

    def test_initialize_atomic_variables(self):
        assert self.get_main('main = "hello";') == 'hello'

    # Estruturas de dados e valores
    # @flag('amarela')
    def test_support_for_list_literals(self):
        assert self.get_main('main = [1, 2, 3];') == [1, 2, 3]
        assert self.get_main('main = [1, 2, add(1, 2)];') == [1, 2, 3]

    @flag('amarela')
    def test_support_for_tuple_literals(self):
        assert self.get_main('main = (1, 2, 3);') == (1, 2, 3)
        assert self.get_main('main = (1, 2, add(1, 2));') == (1, 2, 3)

    #@flag('amarela')
    def test_support_for_record_literals(self):
        assert self.get_main('main = {foo: "bar"};') == {'foo': 'bar'}
        assert self.get_main('main = {foo: add(1, 2)};') == {'foo': 3}

    @flag('branca')
    def test_support_for_attribute_access(self):
        # Somente records possuem atributos
        assert self.get_main('x = {foo: "bar"}; main = x.foo;') == {'foo': 'bar'}['foo']
        assert self.get_main('main = {foo: "bar"}.foo;') == 'bar'

    @flag('amarela')
    def test_support_for_tag_constructor(self):
        assert self.get_main('main = Just 42;') == Just(42)
        assert self.get_main('main = Nothing;') == Nothing

    @flag('vermelha')
    def test_support_for_lambdas(self):
        # Nota: não existem funções de zero argumentos!
        func = self.get_main('main = fn (x) => add(x, x);')
        assert func(1) == 2 and func(2) == 4

        func = self.get_main('main = fn (x, y) => add(x, y);')
        assert func(1, 2) == 3 and func(2, 3) == 5

    # Controle de fluxo
    @flag('preta')
    def test_support_for_let_expressions(self):
        assert self.get_main('main = let x=40; y=2; in x + y;') == 42
        assert self.get_main('''
            main =
               let
                   x = 40;
                   y = 2;
               in add(x, y);
            ''') == 42

    @flag('vermelha')
    def test_grammar_converts_function_defs_in_lambdas(self):
        # Para isso, alguém precisa implementar o let e o lambda!
        assert self.get_main('''
            main =
               let
                   f(x) = add(x, x);
                   y = 1;
               in f(add(10, 1));
            ''') == 42

    @flag('preta')
    def test_support_for_case_expressions_with_no_else_clause(self):
        assert self.get_main('''
            x = Just 42;
            main =
               case x of
                   Just v: v + 1;
                   Nothing: 0;
            ''') == 43

    @flag('vermelha')
    def test_else_clause_in_case_expressions(self):
        # Para isso, alguém precisa implementar o case
        assert self.get_main('''
            x = Just 42;
            main =
               case x of
                   Just v: v + 1;
                   else: 0;
            ''') == 43

    # Operadores
    # @flag('branca')
    def test_support_for_unary_minus(self):
        # Equivalente a chamar a função builtin neg
        assert self.get_main('main = -2;') == -2.0
        assert self.get_main('main = equal(-2, neg(2));')

    # @flag('branca')
    def test_support_for_unary_plus(self):
        # Equivalente a chamar a função builtin pos
        assert self.get_main('main = +2;') == 2.0
        assert self.get_main('main = equal(+2, pos(2));')

    # @flag('branca')
    def test_support_for_unary_not(self):
        # Equivalente a chamar a função builtin negate
        assert self.get_main('main = not true;') is False
        assert self.get_main('main = equal(not true, negate(true));')

    @flag('preta++')
    def test_support_for_arbitrary_binary_operators(self):
        # Mais difícil que parece! Primeiro deve determinar a precedência e
        # associatividade de cada operador. Depois, deve trocar a expressão
        # com operadores pelo seu correspondente como chamada de função.
        assert self.get_main('main = 40 + 2;') == 42
        assert self.get_main('main = "foo" ++ "bar";') == 'foobar'

    @flag('vermelha')
    def test_support_operator_definition(self):
        mod = self.get_mod('left_op 5 (.+) as addv;')
        op = getattr(mod, '__operators')['.+']
        assert isinstance(op, Operator)
        assert callable(op.function)
        assert op.symbol == '.+'
        assert op.precedence == 5
        assert op.assoc == Assoc.LEFT

        mod = self.get_mod('right_op 1 (::) as cons;')
        op = getattr(mod, '__operators')['::']
        assert isinstance(op, Operator)
        assert callable(op.function)
        assert op.symbol == '::'
        assert op.precedence == 5
        assert op.assoc == Assoc.RIGHT

    @flag('vermelha')
    def test_support_operator_defined_with_implicit_precedence(self):
        # Precisa do anterior para funcionar.
        # Os dois juntos valem uma bandeira preta!
        mod = self.get_mod('left_op 5 (.+) as addv;'
                           'right_op (+?) as addm from (.+);')
        op1 = getattr(mod, '__operators')['.+']
        op2 = getattr(mod, '__operators')['+?']
        assert op1.precedence == op2.precedence == 5

    @flag('preta++')
    def test_replaces_binary_operator_by_function_application(self):
        # Precisamos implementar o suporte de operadores antes!
        assert self.get_main('left_op (.+) as add from (+); '
                             'main = 40 .+ 2;') == 42

    # Namespaces
    @flag('amarela')
    def test_support_for_declaring_exporting_variables_and_functions(self):
        # Somente variáveis e funções. Tipos e operadores ficam em outro teste
        assert self.get_mod('export (foo);'
                            'foo = 42;').foo == 42

        mod = self.get_mod('export (foo, bar); '
                           'foo = 40;'
                           'bar = 2;')
        assert mod.foo == 40
        assert mod.bar == 2

    @flag('amarela')
    def test_union_types_export_all_cases(self):
        mod = self.get_mod('export (Foobar); '
                           'type Foobar = Foo | Bar;')
        assert isinstance(mod.Foo, mod.Foobar)
        assert isinstance(mod.Bar, mod.Foobar)

    @flag('amarela')
    def test_exported_operator_also_exports_related_function(self):
        mod = self.get_mod('export (+);')
        assert hasattr(mod, 'add')
        assert '+' in mod.__operators

    @flag('preta')
    def test_support_for_import_all(self):
        # Import * não funciona dentro de funções.
        # Compilador deve avaliar módulo durante a compilação, investigar todos
        # os símbolos públicos (e honrar o atributo __all__) e converter
        # o comando de import para conter os nomes explicitamente.
        # Além do mais, nomes importados explicitamente devem ter prioridade.
        # Deste modo, todos os star imports devem ser realizados no início.
        assert self.get_main('import "math"; '
                             'main = sqrt(4);') == 2

    @flag('vermelha')
    def test_support_for_qualified_import(self):
        # Lembre-se que para funcionar, é necessário exportar o módulo como
        # um dicionário já que acesso a atributo é traduzido para acesso de
        # dicionário. Não é tão difícil já que todos módulos possuem um
        # atributo __dict__ que guarda todas variáveis exportadas.
        assert self.get_main('import "math" as math; '
                             'main = math.sqrt(4);') == 2

    @flag('amarela')
    def test_support_for_explicitly_imported_names(self):
        # Sem suporte para aliasing
        assert self.get_main('import (sqrt) from "math"; '
                             'main = sqrt(4);') == 2

    @flag('amarela')
    def test_support_for_explicitly_imported_names_with_aliases(self):
        assert self.get_main('import (pi, sin as seno) from "math"; '
                             'main = sen(pi);') == 0.0

    # Typedefs
    @flag('vermelha')
    def test_support_type_definition(self):
        # Tipos são criados pela função cremilda.runtime.base.adt.
        # Olhe o código.
        value = self.get_main('type Option = Value Number | Nil;'
                              'main = Value 42')
        assert str(value) == 'Value(42.0)'
        assert isinstance(value, sk.Union)

        value_class = type(value)
        with pytest.raises(ValueError):
            value_class("foo")

    @flag('vermelha')
    def test_support_type_definition_with_generic_type(self):
        # Se colocarmos uma variável como argumento de um tipo, subentende-se
        # que trata-se de um caso que aceita variáveis de qualquer tipo.
        value = self.get_main('type Option = Value a | Nil; '
                              'main = Value 42')
        assert str(value) == 'Value(42.0)'
        assert isinstance(value, sk.Union)

    @flag('amarela')
    def test_exporting_type_also_exports_its_sub_types(self):
        # Precisa da implementação acima para funcionar!
        mod = self.get_mod(
            'export (Option);'
            'type Option = Value x'
            '            | Nil; '
            'main = Value 42'
        )
        assert issubclass(mod.Option, sk.Union)
        assert issubclass(mod.Value, mod.Option)
        assert isinstance(mod.Nil, mod.Option)
        assert mod.Value != mod.Option
        assert mod.Nil != mod.Option
