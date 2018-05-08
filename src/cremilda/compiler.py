import types

from cremilda import tokenize, parse_tokens
from cremilda.ir import internal_representation


def compile_source(src):
    """
    Pipeline básico de um compilador: Cremilda -> Python.
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


def compile_to_module(src, module_name, input_file=None):
    """
    Retorna um objeto módulo.
    """
    input_file = input_file or module_name + '.crem'
    mod = types.ModuleType(module_name)
    py_src = compile_source(src)
    code = compile(py_src, input_file, 'exec')
    exec(code, mod.__dict__)
    return mod
