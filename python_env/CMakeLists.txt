# The produced target will be discarded when this file runs out of scope,
# allowing us to re-find the python executable (this time as a virtual env).
find_package(Python3 3.12 REQUIRED COMPONENTS Interpreter Development)
execute_process(
    COMMAND ${Python3_EXECUTABLE} -m venv "${CMAKE_PYENV}" --copies
    COMMAND_ERROR_IS_FATAL ANY)

# Note: for now -DPython3_SABI_LIBRARY seems to UTTERLY fail on windows.
# TODO: Look into it, because the stable ABI is obviously the better option.
set_target_properties(
    Python3::Module
    PROPERTIES
        IMPORTED_GLOBAL True)
