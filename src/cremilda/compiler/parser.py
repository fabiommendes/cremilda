import ox
from ox.helpers import singleton, identity, cons

from .ast import BinOp, Call, Atom, Name, Enum, Expr, Stmt
from .lexer import tokenize


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
        # ("statement : typedef", identity),
        # ("statement : opdef", identity),
        # ("statement : export", identity),
        # ("statement : import", identity),

        # Definição de tipos
        # ("typedef : ...", ...),

        # Definição de operadores
        # ("opdef : ...", ...),

        # Exports
        # ("export : ...", ...),

        # Imports
        # ("import : ...", ...),

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
        ("elem : value", identity),
        ("elem : value OP value", op_call),
        ("elem : ifexpr", identity),
        ("elem : '+' value", lambda x: Expr.Call(Expr.Name('pos'), [x])),
        ("elem : '-' value", lambda x: Expr.Call(Expr.Name('neg'), [x])),
        ("elem : 'not' value", lambda x: Expr.Call(Expr.Name('negate'), [x])),
        # ("elem : unaryop", identity),
        # ("elem : lambda", identity),
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
        ("atom : TYPENAME", Enum),
        ("atom : NAME", Name),
        ("atom : list", identity),
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
        # ("lambda : ...", ...),

        # If
        ("ifexpr : 'if' value 'then' elem 'else' elem", Expr.If),

        # Let
        # ("letexpr : ...", ...),

        # Case
        # ("caseexpr : ...", ...),

        # Listas
        ("list : '[' ']'", lambda: Expr.List([])),
        ("list : '[' items ']'", lambda x: Expr.List(x)),

        ("items: elem", lambda x: [x]),
        ("items: elem ',' items", lambda x, z: [x, *z]),
        ("items: elem ',' items ','", lambda x, z: [x, *z]),

        # Records
        # ("record : ...", ...),
        ("record : '{' objvalue '}'", lambda y : Expr.Record(y)),
        ("objvalue : NAME ':' elem", lambda x, z : {x:z}),
        ("objvalue : NAME ':' elem ',' objvalue", lambda k, y, z : {k: y, **z}),

        # Construtor
        # ("constructor : ...", ...),
    ])


#
# Funções auxiliares
# ------------------------------------------------------------------------------

# Expr helpers
op_call = (lambda x, op, y: BinOp(op, x, y))


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
