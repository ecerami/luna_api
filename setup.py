"""
Setup Script.
"""

import codecs
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Read in requirements.txt
with codecs.open('requirements.txt') as f:
    requirements = f.read().splitlines()
    install_requires=requirements,

setup(
    name='Luna API',
    description="Luna API",
    long_description="Luna API",
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    version="1.0",
    install_requires=requirements,
    entry_points="""
    [console_scripts]
    luna=luna.cli:cli
    """,
    python_requires=">3.6",
    license='MIT',
    author='Ethan Cerami',
    include_package_data=True
)
