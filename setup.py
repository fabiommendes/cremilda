import sys

from setuptools import setup, find_packages

sys.path.append('src')

setup(
    name='Cremilda',
    package_dir={'': 'src'},
    packages=find_packages('src'),
)
