# Convenience functions for easy CMake configuration.
# Inspired from: https://doc.qt.io/qtforpython-6/examples/example_scriptableapplication_scriptableapplication.html

import argparse
import sys
import os
import glob
import re
import tomllib


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

    res = []
    for key in dev:
        res += deps[key]
    return ';'.join(res)

def find_module(module):
    for p in sys.path:
        if 'site-' in p:
            module = os.path.join(p, module)
            if os.path.exists(module):
                return os.path.realpath(module)
    print(f'Unable to find module {module}.')
    return None

def shiboken_include():
    module = find_module('shiboken6_generator')
    if module is None:
        return None

    result = os.path.join(module, 'include')
    if not os.path.exists(result):
        print(f'Unable to find include directory for module {module}.')
        return None

    return result

def shiboken_library():
    module = find_module('shiboken6')
    if module is None:
        return None

    suffix = ''
    if sys.platform == 'win32':
        suffix = 'lib'
    elif sys.platform == 'darwin':
        suffix = 'dylib'
    # Linux
    else:
        suffix = 'so.*'
    
    pattern = '*.' + suffix
    if sys.platform != 'win32':
        pattern = 'lib' + pattern

    result = glob.glob(os.path.join(module, pattern))
    def predicate(lib):
        basename = os.path.basename(lib)
        if 'shiboken' in basename or 'pyside6' in basename:
            return True
        return False
    result = [lib for lib in result if predicate(lib)]

    if sys.platform == 'win32':
        result = [os.path.realpath(lib) for lib in result]

    return ';'.join(result)

def shiboken_generator():
    module = find_module('shiboken6_generator')
    if module is None:
        return None

    result = os.path.join(module, 'shiboken6')
    if sys.platform == 'win32':
        result += '.exe'

    if not os.path.exists(result):
        print('Unable to locate Shiboken generator')
        return None
    return result


def kwpackval(key, *keys): return {k: key for k in keys}
subparser_props = { 'title': 'queries',
                    'description': 'valid queries',
                    'help': 'additional help',
                    'required': True }


parser = argparse.ArgumentParser()
queries = parser.add_subparsers(**subparser_props)


error_pyproject = ('Unable to process the \'pyproject.toml\' file.'
                   'Make sure the file is present, accessible and valid.')
subparser = queries.add_parser('pyproj',
                               **kwpackval("queries information about the Python project",
                                           'help',
                                           'description')
                               ).add_subparsers(**subparser_props)
subparser.add_parser('deps',
                     **kwpackval("query the project's direct dependencies",
                                 'help',
                                 'description')
                     ).set_defaults(func=python_project_dependencies,
                                    err=error_pyproject)
subparser.add_parser('devdeps',
                     **kwpackval("query the project's development dependencies",
                                 'help',
                                 'description')
                     ).set_defaults(func=python_project_dev_dependencies,
                                    err=error_pyproject)

error_module = ('Did you forget to activate your virtualenv? Or perhaps'
                ' you forgot to build / install PySide6 into your currently active Python'
                ' environment?')
subparser = queries.add_parser('shiboken',
                               **kwpackval("queries information about Shiboken",
                                           'help',
                                           'description')
                               ).add_subparsers(**subparser_props)
subparser.add_parser('generator',
                     **kwpackval("query the Shiboken generator path",
                                 'help',
                                 'description')
                     ).set_defaults(func=shiboken_generator,
                                    err=error_module)
subparser.add_parser('include',
                     **kwpackval("query Shiboken's include directories needed for its generated files",
                                 'help',
                                 'description')
                     ).set_defaults(func=shiboken_include,
                                    err=error_module)
subparser.add_parser('libraries',
                     **kwpackval("query Shiboken's libraries needed for linking its generated files",
                                 'help',
                                 'description')
                     ).set_defaults(func=shiboken_library,
                                    err=error_module)


args = parser.parse_args()
res = args.func()
if res is None:
    sys.exit(args.err)
print(res)
