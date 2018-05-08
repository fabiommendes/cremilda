Cremilda Language
==================

Cremilda* is a minimalist functional educational programming language developed to
teach a compilers course at University of Brasília/Brazil. That's why the rest
of this readme is in Portuguese ;)

*provisional name.

Introdução
==========

Cremilda é uma linguagem de programação funcional com o foco em simplicidade
e facilidade de implementação. O compilador e o runtime da linguagem são em
Python. Muito provavelmente é simples portar o runtime para outras linguagens
dinâmicas e no futuro talvez veremos Cremilda rodando no navegador em
Javascript.

Tipos básicos
-------------

Apenas 2 tipos atômicos: strings, booleanos e números (floats). Estes
tipos podem ser se compor para formar outros tipos algébricos: tuplas, records
e tagged unions::

    # Números podem ser expressos em vários formatos
    x = 42
    y = -3.14
    z = 1.6e-19

    # Strings são delimitadas por aspas duplas
    a = "foo"

    # Booleanos de "Javascript"
    x = true
    y = false

    # Tuplas (em construção)
    x = (1, 2)

    # Listas (simplesmente encadeadas) (em construção)
    x = [1, 2, 3, 4]

    # Records/Structs/Objects (em construção)
    x = {name: "John", age: 42}

    # Tagged unions/Enums (em construção)
    x = Nothing
    y = Just 42 
    


Expressões
----------

Cremilda é uma linguagem baseada em expressões (em oposição à declarações
imperativas). As expressões mais básicas são variáveis, construção de objeto,
chamadas de função e operadores arbitrários::

    # Chamada de função + operadores
    x = sqrt(4) + 1

    # Construindo uma instância de tagged union
    x = Ok "success"
    y = Err "bad request"

    # Note que nomes de variáveis são sempre minúsculos e nomes de tipos
    # aparecem em CamelCase

Números aceitam as operações básicas::

    x = 2 + 1
    y = 2 * 4
    z = 3 ** 2
    w = 4 / 2
    k = 4 - 2

Comparações são feitas com >, <, ==, !=, >=, <=.


Módulos
-------

Um módulo deve declarar as variáveis e operadores na primeira linha::

    export (Bool, name, age, +, -);


Em seguida, declara os imports utilizados::

    import "module";  # todos nomes
    import "module" exposing (Foo, bar, baz);  # especifica alguns nomes
    import "module" exposing (Foo => Foobar, bar, baz);  # importa sob nome diferente

Novos tipos::

    type Vec = (Number, Number);

    # Enums e tagged unions
    type Bool = False | True;
    type Option = Null | Value x;
    type List = Nil | Cons (x, Cons);

Operadores::

    right-operator 9 (:) => cons;
    left-operator 8 (?+) => try_add;
    left-operator 8 (?-) => try_sub;
    left-operator 9 (?*) => try_mul;
    left-operator 9 (?/) => try_div;
    left-operator 9 (|>) => fcall;

Por último, declaramos as constantes e funções do módulo::

    # Constantes
    pi = 3.1415;
    constants_list = Cons (pi, Nil);

    # Funções
    inc(n) = n + 1;


Estruturas de controle
----------------------

Cremilda não possui várias estruturas de controle esperadas em outras linguagens
de programação. No entanto, as poucas oferecidas são mais que o suficiente para
realizar qualquer tipo de computação.

Ifs::

    # else é obrigatório!
    fat(n) = if n < 2 then 1 else n * fat(n);

    # Indentação é irrelevante
    fib(n) =
        if n < 2 then
            1
        else
            fib(n - 1) + fib(n - 2);

    # Com isso, podemos compor várias condições em um único bloco
    quadrant(x, y) =
        if x > 0 and y > 0 then
            1
        else if x < 0 and y < 0 then
            2
        else if x < 0 and y < 0 then
            3
        else if x > 0 and y < 0 then
            4
        else
            0

Blocos de definições::

    # Podemos definir valores intermediários dentro de um block let.
    baskhara(a, b, c) =
        let
            delta = b^2 - 4 * a * c;
            norm = 2 * a;
        in ((-b + sqrt(delta)) / norm, (-b - sqrt(delta)) / norm);


Expressões case::

    fmap(func, x) =
        case x of
            Ok value: Ok func(value);
            Err e: x;


Funções anônimas::

    doubles = x => x + x


Avançado
--------

Acesso a funções do Python::

    concat(x, y) = $str.__add__(x, y)
    add(x, y) = $operator.add(x, y)

