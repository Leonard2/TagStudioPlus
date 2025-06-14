# Convenience functions for easy CMake configuration.
# Inspired from: https://doc.qt.io/qtforpython-6/examples/example_scriptableapplication_scriptableapplication.html

import argparse
import sys
import os
import re
import tomllib
from packaging.version import Version
from packaging.specifiers import SpecifierSet


def python_project_versioncheck():
    with open("pyproject.toml", "rb") as f:
        proj = tomllib.load(f)
    spec = SpecifierSet(proj['project']['requires-python'])
    pyver = Version('.'.join(map(str, sys.version_info[:3])))
    if pyver in spec:
        return spec
    else:
        print(f"Current python version ({pyver}) does not satisfy the project's requirement ({spec}).")
    return None

def python_project_dependencies():
    with open("pyproject.toml", "rb") as f:
        proj = tomllib.load(f)
    return ';'.join(proj['project']['dependencies'])

def python_project_dev_dependencies():
    with open("pyproject.toml", "rb") as f:
        proj = tomllib.load(f)
    # Get the 'dev' entry.
    dev = proj['project']['optional-dependencies']['dev'][0]
    dev = re.search("(?<=tagstudio\\[).*(?=\\])", dev)
    dev = dev.group().split(',')
    # Process the dev entry.
    deps = proj['project']['optional-dependencies']
    deps.pop('dev')

    res = [v for key in dev for v in deps[key]]
    return ';'.join(res)

def find_module(module):
    for p in sys.path:
        if 'site-' in p:
            m = os.path.join(p, module)
            if os.path.exists(m):
                return os.path.realpath(m)
    print(f'Unable to find module {module}.')
    return None


def kwpackval(key, *keys): return {k: key for k in keys}
subparser_props = { 'title': 'queries',
                    'description': 'valid queries',
                    'help': 'additional help',
                    'required': True }


parser = argparse.ArgumentParser()
queries = parser.add_subparsers(**subparser_props)


error_pyproject = ('Unable to process the \'pyproject.toml\' file.\n'
                   'Make sure the file is present, accessible and valid.')
subparser = queries.add_parser('pyproj',
                               **kwpackval("queries information about the Python project",
                                           'help',
                                           'description')
                               ).add_subparsers(**subparser_props)
subparser.add_parser('version',
                     **kwpackval("check the project's required python version",
                                 'help',
                                 'description')
                     ).set_defaults(func=lambda _: python_project_versioncheck(),
                                    err="Error while checking the Python version.")
subparser.add_parser('deps',
                     **kwpackval("query the project's direct dependencies",
                                 'help',
                                 'description')
                     ).set_defaults(func=lambda _: python_project_dependencies(),
                                    err=error_pyproject)
subparser.add_parser('devdeps',
                     **kwpackval("query the project's development dependencies",
                                 'help',
                                 'description')
                     ).set_defaults(func=lambda _: python_project_dev_dependencies(),
                                    err=error_pyproject)

error_module = ('Did you forget to activate your virtualenv?\nOr perhaps'
                ' you forgot to build / install PySide6 into your currently active Python'
                ' environment?')
subparser = queries.add_parser('module',
                               **kwpackval("queries the path for a given Python module",
                                           'help',
                                           'description'))
subparser.add_argument('which',
                       help='which module to query for',
                       choices=['PySide6',
                                'shiboken6',
                                'shiboken6_generator'])
subparser.set_defaults(func=lambda args: find_module(args.which),
                       err=error_module)


args = parser.parse_args()
res = args.func(args)
if res is None:
    sys.exit(args.err)
print(res)
