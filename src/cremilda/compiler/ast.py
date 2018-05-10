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
    Lambda= sk.opt(fargs=list, expr=Expr)
    Op = sk.opt(op=str, left=this, right=this)
    Or = sk.opt(left=this, right=this)
    Record = sk.opt(data=list)
    Tuple = sk.opt(data=tuple)

    def required_symbols(self, acc=None):
        """
        Retorna a lista de símbolos externos necessários para avaliar a
        expressão.
        """
        acc = set() if acc is None else acc
        all_names = self.visit_nodes(required_symbols_visitor, acc)
        lambda_names = self.lambda_symbols()
        print(list(lambda_names))
    
        return all_names.difference(lambda_names)

    def lambda_symbols(self, acc=None):
        acc = set() if acc is None else acc
        return self.visit_nodes(required_lambda_symbols, acc)


class Stmt(Union):
    Assign = sk.opt(name=str, expr=Expr)
    Export = sk.opt(names=list)
    Fundef = sk.opt(name=str, fargs=list, expr=Expr)
    Import = sk.opt(module=str, names=dict)
    ImportAll = sk.opt(module=str)
    Opdef = sk.opt(symbol=str, function=str, assoc=Assoc, precedence=int)
    Typedef = sk.opt(name=str, options=list)

    def required_symbols(self, acc=None):
        acc = set() if acc is None else acc
        if isinstance(self, Assign):
            self.expr.required_symbols(acc)
        elif isinstance(self, Fundef):
            acc.update(self.expr.required_symbols() - set(self.fargs))
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
Op = Expr.Op
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

def required_lambda_symbols(x, acc):
    if isinstance(x, Lambda):
        for arg in x.fargs:
            acc.add(arg)
        return False
