# The produced target will be discarded when this file runs out of scope,
# allowing us to re-find the python executable (this time as a virtual env).
find_package(Python3 3.12 REQUIRED COMPONENTS Interpreter)
execute_process(
    COMMAND ${Python3_EXECUTABLE} -m venv "${CMAKE_PYENV}" --copies
    COMMAND_ERROR_IS_FATAL ANY)
