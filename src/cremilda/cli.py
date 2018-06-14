import inspect
import sys

import click

from .compiler import transpile, compile_module
from .compiler import SemanticError


# Usamos a biblioteca click: http://click.pocoo.org/
@click.command(name='cremilda')
@click.argument('arquivo', type=click.Path('r'))
@click.option('--output', '-o', type=click.File('w', lazy=True), help='arquivo de saída')
@click.option('--run', '-r', help='run file', is_flag=True)
def cremilda(arquivo, output, run):
    """
    Compila ARQUIVO de entrada e salva resultado na SAIDA ou no terminal.
    """

    try:
        main(arquivo, output, run)
    except SemanticError as exc:
        exit('ERROR: %s' % exc)


def main(path, output, run):
    """
    Realiza interação básica da linha de comando.
    """
    with click.open_file(path, 'r') as F:
        source = F.read()

    if run:
        mod = compile_module(source, '__main__', path, load=False)
        run_main_object(getattr(mod, '__main', None))
    else:
        py_source = transpile(source)
        print(py_source, file=output or sys.stdout)


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
