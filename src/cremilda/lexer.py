import ox


class Lexer(ox.Lexer):
    """
    Classe de Lexer, define as tokens aceitas na linguagem.
    """

    # Ignoradas
    _COMMENT = r'\#[^\n]*'

    # Tokens
    NUMBER = r'\d+(\.\d+)?'
    STRING = r'"[^"]*"'
    BOOL = r'true|false'
    EQ = r'='
    SEMICOLON = r';'
    OP = r'([-+*/<>?@&$^~%][-+*/<>?@&$^~%=]*|==)'
    LPAR = r'\('
    RPAR = r'\)'
    NAME = r'[a-z_]+'
    TYPENAME = r'[A-Z][a-z_]*'
    COMMA = r'\,'

    # Palavras reservadas
    r_IF = 'if'
    r_THEN = 'then'
    r_ELSE = 'else'


#
# Funções públicas
# ------------------------------------------------------------------------------
tokenize = Lexer.make_lexer()
lexemes = (lambda src: [tk.value for tk in tokenize(src)])
tok_types = (lambda src: [tk.type for tk in tokenize(src)])
