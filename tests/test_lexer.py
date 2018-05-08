from cremilda.lexer import tokenize, lexemes, tok_types


def test_lex_fat_example(fat_source):
    lst = 'fat ( n ) = if n < 1 then 1 else n * fat ( n - 1 ) ;'.split()
    toks = 'NAME LPAR NAME RPAR EQ IF NAME OP NUMBER THEN NUMBER ELSE ' \
           'NAME OP NAME LPAR NAME OP NUMBER RPAR SEMICOLON'.split()
    assert lexemes(fat_source) == lst
    assert tok_types(fat_source) == toks
