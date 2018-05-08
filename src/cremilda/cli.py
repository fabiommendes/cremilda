import inspect
import sys

import click

from cremilda.compiler import compile_source


# Usamos a biblioteca click: http://click.pocoo.org/
@click.command(name='cremilda')
@click.argument('arquivo', type=click.Path('r'))
@click.option('--output', '-o', type=click.File('w', lazy=True), help='arquivo de saída')
@click.option('--run', '-r', help='run file', is_flag=True)
def cremilda(arquivo, output, run):
    """
    Compila ARQUIVO de entrada e salva resultado na SAIDA ou no terminal.
    """
    main(arquivo, output, run)


def main(path, output, run):
    """
    Realiza interação básica da linha de comando.
    """
    with click.open_file(path, 'r') as F:
        source = F.read()
    result = compile_source(source)

    if run:
        namespace = {}
        code = compile(result, path, 'exec')
        exec(code, namespace)
        run_main_object(namespace.get('__main'))
    else:
        print(result, file=output or sys.stdout)


def run_main_object(main):
    """
    Roda o objeto "main".
    """
    if main is None:
        click.secho('Warning:', fg='yellow', bold=True, nl=False)
        click.echo(' main function is not defined')
    elif isinstance(main, str):
        print(main)
    elif callable(main):
        args = [input('%s: ' % x) for x in get_func_args(main)]
        result = main(*args)
        print(result)
    else:
        print('result: %s' % main)


def get_func_args(func):
    sig = inspect.signature(func)
    return sig.parameters.values()
