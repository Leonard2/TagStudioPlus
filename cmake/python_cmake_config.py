# Convenience functions for easy CMake configuration.
# Inspired from: https://doc.qt.io/qtforpython-6/examples/example_scriptableapplication_scriptableapplication.html

import sys
import os
import glob
import re
import tomllib


error_pyproject = ('Unable to process the \'pyproject.toml\' file.'
                   'Make sure the file is present, accessible and valid.')
error_module = ('Did you forget to activate your virtualenv? Or perhaps'
                ' you forgot to build / install PySide6 into your currently active Python'
                ' environment?')

# option, function, error, description
options = {}

options.update({"--python-project-dependencies":
                (lambda: python_project_dependencies(),
                error_pyproject,
                "Print current Python project dependencies.")})
options.update({"--python-project-dev-dependencies":
                (lambda: python_project_dev_dependencies(),
                error_pyproject,
                "Print current Python project optional dev dependencies.")})
options.update({"--shiboken-include":
                (lambda: shiboken_include(),
                error_module,
                "Print the include directory necessary for Shiboken-generated files.")})
options.update({"--shiboken-library":
                (lambda: shiboken_library(),
                error_module,
                "Print the path to the shared libraries necessary for Shiboken-generated files.")})
options.update({"--shiboken-generator":
                (lambda: shiboken_generator(),
                error_module,
                "Print the path to the Shiboken generator.")})
usage = ""
options.update({"-h":
                (lambda: usage,
                "",
                "Show command line usage.")})
options.update({0:
                (lambda: print(usage),
                 "Invalid options.",
                 "")})


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


options_usage = ''
for i, (flag, (_, _, description)) in enumerate(options.items()):
    if flag != 0:
        options_usage += f'    {flag:<45} {description}'
    if i < len(options) - 1:
        options_usage += '\n'

usage = f"""
Utility to determine various Python config options for CMake projects.

Usage: python_cmake_config.py [option]
Options:
{options_usage}
"""

option = sys.argv[1] if len(sys.argv) == 2 else 0
handler, error, _ = options.get(option, options[0])
handler_result = handler()
if handler_result is None:
    sys.exit(error)
print(handler_result)
