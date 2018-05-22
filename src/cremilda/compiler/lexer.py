import ox


class Lexer(ox.Lexer):
    """
    Classe de Lexer, define as tokens aceitas na linguagem.
    """

    # Ignoradas
    _COMMENT = r'\#[^\n]*'

    # Tokens
    STRING = r'"([^\n"](\\")?)*"'
    NUMBER = r'\d+(\.\d+)?([eE][+-]?\d+)?'
    NAME = r'[a-z_][a-z0-9_]*'
    TYPENAME = r'[A-Z][a-zA-Z0-9]*'
    OP = (r'[.=:][-+*/<>?@&$^~%=:]+'
          r'|[-+*/<>?@&$^~%][-+*/<>?@&$^~%=:]*')
    CONTROL = r'[[\](){},;:=]'

    # Palavras reservadas
    r_TRUE = r'true'
    r_FALSE = r'false'
    r_IF = r'if'
    r_THEN = r'then'
    r_ELSE = r'else'
    r_IMPORT = r'import'
    r_FROM = r'from'


#
# Funções públicas
# ------------------------------------------------------------------------------
tokenize = Lexer.make_lexer()
lexemes = (lambda src: [tk.value for tk in tokenize(src)])
tok_types = (lambda src: [tk.type for tk in tokenize(src)])
