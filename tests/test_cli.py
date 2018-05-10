import contextlib
import io
import sys

import builtins
import mock

from cremilda.cli import run_main_object


@contextlib.contextmanager
def capture_input():
    file = io.StringIO()
    stdout = sys.stdout

    try:
        sys.stdout = file
        yield file
    finally:
        sys.stdout = stdout


def test_run_main_string():
    with capture_input() as stdout:
        run_main_object('foo')
    assert stdout.getvalue() == 'foo\n'


def test_run_main_func():
    def double(x):
        return 2 * x

    with mock.patch.object(builtins, 'input', lambda x: 21):
        with capture_input() as stdout:
            run_main_object(double)
    assert stdout.getvalue() == '42\n'


def test_run_main_value():
    with capture_input() as stdout:
        run_main_object(42)
    assert stdout.getvalue() == 'result: 42\n'


def test_run_without_main_function():
    with capture_input() as stdout:
        run_main_object(None)
    assert stdout.getvalue() == 'Warning: main function is not defined\n'
