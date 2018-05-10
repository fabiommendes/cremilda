import sys
import types

from .ir import internal_representation
from .lexer import tokenize
from .parser import parse_tokens


def transpile(src):
    """
    Pipeline básico de um compilador.

    Converte código Cremilda para Python.
    """

    # Análise léxica
    tokens = tokenize(src)

    # Análise sintática
    ast = parse_tokens(tokens)

    # Converte para representação interna
    ir = internal_representation(ast)

    # Análise semântica
    ir.semantic_analysis()

    # Modifica representação interna para gerar código válido
    ir.transform_ir()

    # Otimizações
    ir.optimize()

    # Emissão de código para o backend (árvores sintáticas Python)
    py_ast = ir.to_python()

    # Emissão de código final
    return py_ast.source()


def compile_module(src, module_name, input_file=None, load=True):
    """
    Compila código e retorna um módulo Python equivalente.

    Se load=True (padrão), registra o módulo como importável por qualquer
    outro módulo Python.

    Exemplo:

        Cria módulo simples

        >>> src = 'export (incr); incr(x) = x + 1;'
        >>> mod = load_module(src, 'my_mod')
        >>> mod.incr(41)
        42

        O módulo fica disponível para importação

        >>> from my_mod import incr
        >>> incr(41)
        42
    """

    # Aceita entradas do tipo file
    if hasattr(src, 'read'):
        input_file = input_file or getattr(src, 'name', None)
        src = src.read()

    # Transpila código fonte
    input_file = input_file or module_name + '.crem'
    py_src = transpile(src)
    code = compile(py_src, input_file, 'exec')

    # Cria módulo
    mod = types.ModuleType(module_name)

    # Executa, salvando os resultados no escopo do módulo
    print(py_src)
    exec(code, mod.__dict__)

    # Registra o módulo globalmente
    if load:
        sys.modules[module_name] = mod

    return mod
