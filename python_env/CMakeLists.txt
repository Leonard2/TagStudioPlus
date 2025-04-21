# The produced target will be discarded when this file runs out of scope,
# allowing us to re-find the python executable (this time as a virtual env).
find_package(Python3 3.12 REQUIRED COMPONENTS Interpreter Development.Module Development.SABIModule)
execute_process(
    COMMAND ${Python3_EXECUTABLE} -m venv "${CMAKE_PYENV}" --copies
    COMMAND_ECHO STDOUT
    COMMAND_ERROR_IS_FATAL ANY)

set_target_properties(
    Python3::Module
    PROPERTIES
        IMPORTED_GLOBAL True)
set_target_properties(
    Python3::SABIModule
    PROPERTIES
        IMPORTED_GLOBAL True
        # On windows, the SABI module is merely a "forwarding DLL", meaning
        # it still requires the non-stable one.
        # At a quick glance, this also seems to be the case for other platforms.
        IMPORTED_LINK_DEPENDENT_LIBRARIES Python3::Module)
