import ox
from ox.helpers import singleton, identity, cons

from .ast import BinOp, Call, Atom, Name, Enum, Expr, Stmt, Lambda, Constructor
from .lexer import tokenize

from cremilda.runtime import Nothing

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
        ("import : 'import' '(' NAME ')' 'from' STRING", lambda x, y: Stmt.Import(y[1:-1], {x: x})),

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
        ("elem : value OP value", op_call),
        ("elem : ifexpr", identity),
        ("elem : '+' value", lambda x: Expr.Call(Expr.Name('pos'), [x])),
        ("elem : '-' value", lambda x: Expr.Call(Expr.Name('neg'), [x])),
        ("elem : 'not' value", lambda x: Expr.Call(Expr.Name('negate'), [x])),
        ("elem : JUST value", lambda x, y: Expr.Call(Expr.Name(str(x)), [y])),
        ("elem : NOTHING", lambda x: Expr.Name(str(x))),
        # ("elem : unaryop", identity),
        # ("elem : constructor", identity),

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
