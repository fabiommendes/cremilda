import sidekick as sk
from ox.union import Union

from ..runtime.base import Assoc

this = object


class Expr(Union):
    And = sk.opt(left=this, right=this)
    Atom = sk.opt(object)
    BinOp = sk.opt(op=str, left=this, right=this)
    Call = sk.opt(caller=this, fargs=list)
    Case = sk.opt(value=this, cases=dict)
    Classname = sk.opt(str)
    Constructor = sk.opt(classname=str, value=this)
    Enum = sk.opt(name=str)
    If = sk.opt(cond=this, then=this, other=this)
    Let = sk.opt(expr=this, binds=dict)
    List = sk.opt(data=list)
    Name = sk.opt(str)
    Not = sk.opt(this)
    Lambda = sk.opt(fargs=list, expr=Expr)
    OpChain = sk.opt(value=list)
    Or = sk.opt(left=this, right=this)
    Record = sk.opt(data=dict)
    Tuple = sk.opt(data=tuple)

    def required_symbols(self, acc=None):
        """
        Retorna a lista de símbolos externos necessários para avaliar a
        expressão.
        """
        acc = set() if acc is None else acc
        if isinstance(self, Lambda):
            print(self.expr.required_symbols())
            acc.update(self.expr.required_symbols() - set(self.fargs))
        else:
            self.visit_nodes(required_symbols_visitor, acc)
        return acc


class Stmt(Union):
    Assign = sk.opt(name=str, expr=Expr)

    # names : lista de strings com os símbolos exportados
    Export = sk.opt(names=list)

    # name  :  nome da função
    # farsg : lista de strings com o nome de cada argumento
    # expr  : corpo da função
    Fundef = sk.opt(name=str, fargs=list, expr=Expr)

    # module : nome do módulo
    # names  : dicionário de nome original para alias de todos
    #          valores importados
    Import = sk.opt(module=str, names=list)

    # module : nome do módulo
    ImportAll = sk.opt(module=str)

    # symbol     : símbolo do operador (ex: '+')
    # function   : nome da função responsável por implementar o operador
    # assoc      : associatividade (esquerda ou direita)
    # precedence : nível de precedência do operador
    Opdef = sk.opt(symbol=str, function=str, assoc=Assoc, precedence=int)

    # name    : nome do tipo
    # options : mapa com o nome de cada opção associada às variáveis
    #           exigidas pelo construtor
    Typedef = sk.opt(name=str, options=dict)

    def required_symbols(self, acc=None):
        acc = set() if acc is None else acc

        if self.is_assign:
            self.expr.required_symbols(acc)
        elif self.is_fundef:
            acc.update(self.expr.required_symbols() - set(self.fargs))
        elif self.is_export:
            acc.update(self.names)
        elif self.is_opdef:
            acc.add(self.function)
        return acc


# Expressões
And = Expr.And
Atom = Expr.Atom
BinOp = Expr.BinOp
Call = Expr.Call
Case = Expr.Case
Classname = Expr.Classname
Constructor = Expr.Constructor
Enum = Expr.Enum
If = Expr.If
Let = Expr.Let
Lambda = Expr.Lambda
List = Expr.List
Name = Expr.Name
Not = Expr.Not
OpChain = Expr.OpChain
Or = Expr.Or
Record = Expr.Record
Tuple = Expr.Tuple

# Declarações
Assign = Stmt.Assign
Export = Stmt.Export
Fundef = Stmt.Fundef
Import = Stmt.Import
ImportAll = Stmt.ImportAll
Opdef = Stmt.Opdef
Typedef = Stmt.Typedef


def required_symbols_visitor(x, acc):
    if isinstance(x, (Name, Classname)):
        acc.add(x.value)
        return False
    elif isinstance(x, Let):
        for stmt in x.binds.values():
            stmt.visit_nodes(required_symbols_visitor, acc)
