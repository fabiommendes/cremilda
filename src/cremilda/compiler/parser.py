import ox
from ox.helpers import singleton, identity, cons

from .ast import BinOp, Call, Atom, Name, Enum, Expr, Stmt, Lambda
from .lexer import tokenize
from ..runtime.builtins import __default_operators as OPERATORS
from ..runtime.base import Assoc



#
# Gramática
# ------------------------------------------------------------------------------
def make_parser():
    return ox.make_parser([
        # Um módulo é uma lista de declarações
        ("module : statement ';'", singleton),
        ("module : statement ';' module", cons),

        # Declarações
        ("statement : vardef", identity),
        ("statement : fundef", identity),
        ("statement : typedef", identity),
        ("statement : import", identity),
        # ("statement : opdef", identity),
        # ("statement : export", identity),

        # Definição de tipos
        ("typedef : 'type' TYPENAME '=' casedeflist", handle_type),
        ("casedeflist : casedef", singleton),
        ("casedeflist : casedef '|' casedeflist", cons),
        ("casedef : TYPENAME TYPENAME", lambda x, y: (x, y)),
        ("casedef : TYPENAME", lambda x: (x, None)),
        
        # Definição de operadores
        # ("opdef : ...", ...),

        # Exports
        # ("export : ...", ...),

        # Imports
        ("import : 'import' '(' list_names ')' 'from' STRING", handle_list_imports_module),
        ("list_names : NAME ',' list_names", lambda x, xs: [x, *xs]),
        ("list_names : NAME 'as' NAME ',' list_names", lambda x, name, xs: [{x: name}, *xs]),
        ("list_names : NAME 'as' NAME", lambda x, name: [{x: name}]),
        ("list_names : NAME", identity),

        # Declaração de funções e variáveis
        ("vardef  : NAME '=' expr", Stmt.Assign),
        ("fundef  : NAME '(' defargs ')' '=' expr", Stmt.Fundef),
        ("defargs : NAME", singleton),
        ("defargs : NAME ',' defargs", cons),

        # Expressões
        ("expr : elem", identity),
        # ("expr : letexpr", identity),
        # ("expr : caseexpr", identity),

        # Elementos
        ("elem : lambda", identity),
        ("elem : value", identity),
        ("elem : opchain", handle_operators),
        ("elem : ifexpr", identity),
        ("elem : '+' value", lambda x: Expr.Call(Expr.Name('pos'), [x])),
        ("elem : '-' value", lambda x: Expr.Call(Expr.Name('neg'), [x])),
        ("elem : 'not' value", lambda x: Expr.Call(Expr.Name('negate'), [x])),
        ("elem : JUST value", lambda x, y: Expr.Call(Expr.Name(str(x)), [y])),
        ("elem : NOTHING", lambda x: Expr.Name(str(x))),
        # ("elem : unaryop", identity),
        # ("elem : constructor", identity),

        # Operadores válidos
        ("op : OP", identity),
        ("op : '+'", lambda: '+'),
        ("op : '-'", lambda: '-'),
        ("opchain : value op value", lambda x, y, z: [x, y, z]),
        ("opchain : value op opchain", lambda x, y, z: [x, y, *z]),

        # Valores
        ("value : atom", identity),
        ("value : fcall", identity),
        ("value : '(' expr ')'", identity),
        # ("value : getattr", identity),

        # Valores atômicos
        ("atom : NUMBER", lambda x: Atom(float(x))),
        ("atom : STRING", lambda x: Atom(x[1:-1])),
        ("atom : TRUE", lambda x: Atom(True)),
        ("atom : FALSE", lambda x: Atom(False)),
        ("atom : TYPENAME", Name),
        ("atom : TYPENAME atom", handle_type_creation),
        ("atom : NAME", Name),
        ("atom : list", identity),
        ("atom : tuple", identity),
        ("atom : record", identity),

        # Chamada de função
        ("fcall : value '(' ')'", lambda x: Call(x, [])),
        ("fcall : value '(' fargs ')'", Call),
        # ("fcall : value LPAR letexpr RPAR", fcallexpr),
        # ("fcall : value LPAR caseexpr RPAR", fcallexpr),
        ("fargs : elem", singleton),
        ("fargs : elem ',' fargs", cons),

        # Acesso a atributo
        # ("getattr : ...", ...),

        # Operadores unários
        # ("unary : ...", ...),

        # Lambdas
        ("lambda : 'fn' '(' defargs ')' '=>' expr", lambd_def),

        # If
        ("ifexpr : 'if' value 'then' elem 'else' elem", Expr.If),

        # Let
        # ("letexpr : ...", ...),

        # Case
        # ("caseexpr : ...", ...),

        # Listas/Tuplas
        ("list : '[' ']'", lambda: Expr.List([])),
        ("list : '[' items ']'", lambda x: Expr.List(x)),
        ("tuple : '(' ')'", lambda: Expr.Tuple(())),
        ("tuple : '(' elem ',' items ')'", lambda x, xs: Expr.Tuple((x, *xs))),

        ("items: elem", lambda x: [x]),
        ("items: elem ',' items", lambda x, z: [x, *z]),
        ("items: elem ',' items ','", lambda x, z: [x, *z]),

        # Records
        ("record : '{' objvalue '}'", lambda y: Expr.Record(y)),
        ("objvalue : NAME ':' elem", lambda x, z: {x: z}),
        ("objvalue : NAME ':' elem ',' objvalue", lambda k, y, z: {k: y, **z}),
    ])


#
# Funções auxiliares
# ------------------------------------------------------------------------------

# Expr helpers
op_call = (lambda x, op, y: BinOp(op, x, y))
lambd_def = (lambda args, expr: Lambda(args, expr))


def handle_type(name, definitions):
    deflist = List([List([Atom(x), Atom(y)]) for x, y in definitions])
    return Stmt.Assign(name, Call(Name('__create_type'), [Atom(name), deflist]))    


def handle_type_creation(name, expr):
    return Call(Name(name), [expr])


def handle_list_imports_module(list_imports, module):
    if isinstance(list_imports, str):
        return Stmt.Import(module[1:-1], [list_imports])
    elif isinstance(list_imports, list):
        return Stmt.Import(module[1:-1], [*list_imports])


from pprint import pprint
def handle_operators(chain):
    # Caso trivial com apenas 1 operador
    if len(chain) == 3:
        x, op, y = chain
        op_info = OPERATORS[op]
        func_name = op_info.function
        return Call(Name(func_name), [x, y])

    # Todos operadores sao iguais: testamos a associatividade
    ops = [OPERATORS[op] for op in chain[1::2]]
    if len(set(ops)) == 1:
        op_info, = set(ops)
        func_name = op_info.function
        operands = chain[0::2]

        if op_info.assoc == Assoc.LEFT:
            x, y, *operands = operands
            expr = Call(Name(func_name), [x, y])
            while operands:
                z = operands.pop(0)
                expr = Call(Name(func_name), [expr, z])
            return expr
        
        else:
            y = operands.pop()
            x = operands.pop()
            expr = Call(Name(func_name), [x, y])
            while operands:
                z = operands.pop()
                expr = Call(Name(func_name), [z, expr])
            return expr

    # Problema arbitrário: níveis de precedencia distintos
    idx, op = max(enumerate(ops), key=lambda x: x[1].precedence)

    pprint(locals())
    raise SystemExit(1)


#
# Cria parser
# ------------------------------------------------------------------------------
def parse(src):
    """
    Realiza análise sintática de uma string de código Cremilda.
    """

    tokens = tokenize(src)
    return parse_tokens(tokens)


parse_tokens = make_parser()
