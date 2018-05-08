from sidekick import record as _record, Maybe, Result, List

# Tipos básicos
Float = float
Bool = bool
String = str
Tuple = tuple
Record = _record

# Tagged unions
Maybe = Maybe
Just, Nothing = Maybe.Just, Maybe.Nothing

Result = Result
Ok, Err = Result.Ok, Result.Err

List = List
Cons, Nil = List.Cons, List.Nil
