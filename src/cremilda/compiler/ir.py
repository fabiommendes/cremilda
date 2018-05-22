from ox.backend.python import block, let, var, return_, function, import_from
from ox.backend.python.ast_statement import as_stmt

from .ast import Fundef, Assign, Typedef, Name, Import
from .emitter import to_python
from .semantic_analysis import SemanticAnalysis, SemanticError


def internal_representation(statements):
    """
    Inicializa módulo a partir de lista de declarações.
    """

    functions = {}
    constants = {}
    imports = {}
    operators = {}
    typedefs = {}
    exports = {}
    symbols = []

    for stmt in statements:
        if isinstance(stmt, Fundef):
            functions[stmt.name] = stmt
            symbols.append(stmt.name)

        elif isinstance(stmt, Assign):
            constants[stmt.name] = stmt.expr
            symbols.append(stmt.name)

        elif isinstance(stmt, Import):
            imports[stmt.module] = stmt
        
        elif isinstance(stmt, Typedef):
            ...

        else:
            raise NotImplementedError('unknown statement: %s' % stmt)

    return Module(
        exposing=exports, 
        imports=imports, 
        typedefs=typedefs,
        operators=operators, 
        functions=functions, 
        constants=constants,
        symbols=symbols,
    )


class Module:
    """
    Representa um módulo Cremilda.

    Attributes:
        functions (dict):
            Um dicionário mapeando nomes de funções às suas respectivas
            definições.
        constants (dict):
            Um dicionário mapeando nomes de funções às suas respectivas
            expressões.
    """

    def __init__(self, exposing=None, imports=None, typedefs=None,
                 operators=None, functions=None, constants=None, symbols=None):
        self.exposing = set(exposing or {})
        self.imports = dict(imports or {})
        self.typedefs = dict(typedefs or {})
        self.operators = dict(operators or {})
        self.functions = dict(functions or {})
        self.constants = dict(constants or {})
        self.symbols = list(symbols or [])

    #
    # Transformações do código
    #
    def semantic_analysis(self):
        """
        Análise semântica.

        Levanta SyntaxError caso alguma inconsistência seja encontrada no
        código.
        """
        analysis = SemanticAnalysis(self)
        analysis.run()

    def transform_ir(self):
        """
        Realiza as alterações necessárias na representação interna para que
        seja possível emitir código Python válido ao final.
        """
        if 'main' in self.get_module_symbols():
            self.constants['__main'] = Name('main')
            self.exposing.add('__main')

    def optimize(self):
        """
        Modifica representação interna para emitir código mais eficiente.
        """

    def to_python(self):
        """
        Cria um módulo Python correspondente ao módulo atual.

        Retorna uma AST Python. O módulo criado possui uma estrutura semelhante
        à forma abaixo::

            def _module():
                # imports, typedefs, funções, etc
                return {'export1': export1, ...}

            globals().update(_module())
        """
        module_func_body = (
            *cremilda_default_imports(self.get_default_imports()),
            *to_python_imports(self.imports),
            *to_python_typedefs(self.typedefs),
            *to_python_operators(self.operators),
            *to_python_functions(self.functions),
            *to_python_constants(self.constants),
            return_({x: var(x) for x in self.exposing}),
        )

        module_func = function._module()[module_func_body]
        stmt = as_stmt(var.globals().method('update', var._module()))
        return block([module_func, stmt])

    #
    # Informações sobre a RI
    #
    def get_module_symbols(self):
        """
        Retorna conjunto de variáveis utilizadas internamente.
        """
        list_imports = []
        for module, import_node in self.imports.items():
            list_imports.append(module)
            for k, v in import_node.names.items():
                list_imports.append(v)
        return {*self.functions, *self.constants, *self.typedefs, *list_imports}

    def get_default_imports(self):
        """
        Retorna a lista de funções do módulo runtime que deve ser importada.
        """
        acc = set()
        for store in (self.functions, self.constants, self.imports):
            for expr in store.values():
                expr.required_symbols(acc)

        acc.difference_update(self.get_module_symbols())
        return acc


def to_python_constants(constants):
    """
    Converte um dicionário mapeando {nome: expr} para atribuições de variável
    em Python.
    """
    return [let(k, to_python(v)) for k, v in constants.items()]


def to_python_functions(functions):
    """
    Converte uma lista de definições de funções para as declarações
    correspondentes em Python.
    """
    py_funcs = []
    for name, func in functions.items():
        name, args, body = func.args
        expr = to_python(body)
        py_funcs.append(function[name](*args)[return_(expr)])
    return py_funcs


def to_python_imports(imports):
    """
    Converte os imports para comandos de importação no Python.
    """
    py_imports = []
    for name, imp in imports.items():
        py_imports.append(to_python(imp))
    return py_imports


def to_python_typedefs(typedefs):
    return []


def to_python_operators(operators):
    return []


def cremilda_default_imports(names):
    """
    Importa todos os nomes do módulo runtime.
    """
    return [import_from('cremilda.runtime', names)]
