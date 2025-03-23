project(TagStudio)


# Install modules necessary for running the python app.
execute_process(
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/cmake/python_cmake_config.py" "--python-project-dependencies"
    OUTPUT_VARIABLE CMAKE_PYENV_DEPENDENCIES
    OUTPUT_STRIP_TRAILING_WHITESPACE
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMAND_ERROR_IS_FATAL ANY)
# We need to remove this entry to avoid conflicting with self-built PySide (if used).
list(FILTER CMAKE_PYENV_DEPENDENCIES EXCLUDE REGEX "PySide6*")
execute_process(
    COMMAND "${Python3_EXECUTABLE}" -m pip install ${CMAKE_PYENV_DEPENDENCIES}
    COMMAND_ERROR_IS_FATAL ANY)
# Install development python modules.
if (NOT DEFINED NO_PYTHON_DEVTOOLS)
    execute_process(
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/cmake/python_cmake_config.py" "--python-project-dev-dependencies"
        OUTPUT_VARIABLE CMAKE_PYENV_DEV_DEPENDENCIES
        OUTPUT_STRIP_TRAILING_WHITESPACE
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        COMMAND_ERROR_IS_FATAL ANY)
    execute_process(
        COMMAND "${Python3_EXECUTABLE}" -m pip install ${CMAKE_PYENV_DEV_DEPENDENCIES}
        COMMAND_ERROR_IS_FATAL ANY)
endif()

file(GLOB_RECURSE PYMODULE_SRC CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/*")
set(STAMP_FILE "${CMAKE_CURRENT_BINARY_DIR}/pymodule.stamp")
# Note: PyInstaller seems to be unable to handle a debug Python.
add_custom_command(
    VERBATIM
    DEPENDS ${PYMODULE_SRC}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMAND Python3::InterpreterMultiConfig
    "-m" "PyInstaller" "${CMAKE_SOURCE_DIR}/tagstudio.spec"
    "-y" "--distpath" ${CMAKE_BINARY_DIR} "--workpath" ${CMAKE_CURRENT_BINARY_DIR}
    COMMAND ${CMAKE_COMMAND} -E touch ${STAMP_FILE}
    OUTPUT ${STAMP_FILE})
add_custom_target(TagStudio
    ALL
    DEPENDS ${STAMP_FILE}
    SOURCES ${PYMODULE_SRC})
