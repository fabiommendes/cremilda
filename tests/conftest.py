import os

import fs.osfs
import pytest


#
# Examples_dir
#
@pytest.fixture(scope='session')
def examples_dir():
    return fs.osfs.OSFS(os.path.dirname(os.path.dirname(__file__))).opendir('examples')


@pytest.fixture(scope='session')
def src(examples_dir):
    return lambda x: examples_dir.gettext(x + '.crm')


@pytest.fixture(scope='session')
def fat_source(examples_dir):
    return examples_dir.gettext('fat.crm')


@pytest.fixture(scope='session')
def hello_source(examples_dir):
    return examples_dir.gettext('hello.crm')


@pytest.fixture(scope='session')
def hellos_source(examples_dir):
    return examples_dir.gettext('hellos.crm')


@pytest.fixture(scope='session')
def funcall_source(examples_dir):
    return examples_dir.gettext('funcall.crm')


@pytest.fixture(scope='session')
def op_source(examples_dir):
    return examples_dir.gettext('op.crm')
