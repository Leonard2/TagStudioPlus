# Convenience functions for easy CMake configuration.
# Inspired from: https://doc.qt.io/qtforpython-6/examples/example_scriptableapplication_scriptableapplication.html

import sys
import re
import tomllib


error_pyproject = ('Unable to process the \'pyproject.toml\' file.'
                   'Make sure the file is present, accessible and valid.')

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
