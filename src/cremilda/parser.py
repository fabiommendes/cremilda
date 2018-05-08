import ox
from ox.helpers import singleton, identity, cons

from .ast import BinOp, Call, Atom, Name, Assign, Enum, Fundef, Expr
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
        ("vardef  : NAME EQ expr", vardef),
        ("fundef  : NAME LPAR defargs RPAR EQ expr", fundef),
        ("defargs : NAME", lambda x: [x]),
        ("defargs : NAME COMMA defargs", lambda x, _, xs: [x, *xs]),

        # Expressões
        ("expr : elem", identity),
        # ("expr : letexpr", identity),
        # ("expr : caseexpr", identity),

        # Elementos
        ("elem : value", identity),
        ("elem : value OP value", op_call),
        ("elem : ifexpr", identity),
        # ("elem : unaryop", identity),
        # ("elem : lambda", identity),
        # ("elem : constructor", identity),

        # Valores
        ("value : atom", identity),
        ("value : fcall", identity),
        ("value : LPAR expr RPAR", lambda x, y, z: y),
        # ("value : getattr", identity),

        # Valores atômicos
        ("atom : NUMBER", lambda x: Atom(float(x))),
        ("atom : STRING", lambda x: Atom(x[1:-1])),
        ("atom : BOOL", lambda x: Atom(x == "true")),
        ("atom : TYPENAME", Enum),
        ("atom : NAME", Name),
        # ("atom : list", identity),
        # ("atom : record", identity),

        # Chamada de função
        ("fcall : value LPAR RPAR", lambda x, y, z: Call(x, [])),
        ("fcall : value LPAR fargs RPAR", fcall),
        # ("fcall : value LPAR letexpr RPAR", fcallexpr),
        # ("fcall : value LPAR caseexpr RPAR", fcallexpr),
        ("fargs : elem COMMA fargs", lambda x, _, xs: [x, *xs]),
        ("fargs : elem", lambda x: [x]),

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
        # ("list : ...", ...),

        # Records
        # ("record : ...", ...),

        # Construtor
        # ("constructor : ...", ...),
    ])


#
# Funções auxiliares
# ------------------------------------------------------------------------------

# Expr helpers
op_call = (lambda x, op, y: BinOp(op, x, y))
fcall = (lambda x, y, z, w: Call(x, z))

# Statement helpers
statements = (lambda x, _, xs: [x, *xs])
vardef = (lambda name, eq, expr: Assign(name, expr))
fundef = (lambda *args: Fundef(args[0], args[2], args[-1]))


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
