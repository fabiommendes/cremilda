from cremilda.compiler.lexer import lexemes, tok_types


def check_values(st, type):
    lst = st.split()
    assert lexemes(st) == lst
    for x in tok_types(st):
        assert x == type


class TestSimpleExpressions:
    def test_lex_atoms(self):
        check_values('"hello" "world"', 'STRING')
        check_values('0 1 0.1 1e-10', 'NUMBER')
        check_values('foo foo1 foo_bar', 'NAME')
        check_values('Foo FooBar FooBar2', 'TYPENAME')

    def test_operators(self):
        check_values("+ - / * ? < >", 'OP')
        check_values(".+ == := <:", 'OP')

    def test_control_chars(self):
        check_values('( ) { } [ ] , ; : =', 'CONTROL')


def test_lex_fat_example(fat_source):
    lst = 'fat ( n ) = if n < 1 then 1 else n * fat ( n - 1 ) ;'.split()
    toks = 'NAME CONTROL NAME CONTROL CONTROL IF NAME OP NUMBER THEN NUMBER ELSE ' \
           'NAME OP NAME CONTROL NAME OP NUMBER CONTROL CONTROL'.split()
    assert lexemes(fat_source) == lst
    assert tok_types(fat_source) == toks
