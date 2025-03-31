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
set(STAMP_DIR "${CMAKE_CURRENT_BINARY_DIR}/pymodule_stamp")
# Note: PyInstaller seems to be unable to handle a debug Python.
add_custom_command(
    VERBATIM
    USES_TERMINAL
    DEPENDS ${PYMODULE_SRC}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMAND Python3::InterpreterMultiConfig
    "-m" "PyInstaller" "${CMAKE_SOURCE_DIR}/tagstudio.spec"
    "-y" "--distpath" ${CMAKE_BINARY_DIR} "--workpath" ${CMAKE_CURRENT_BINARY_DIR}
    "--" "--cppready"
    COMMAND ${CMAKE_COMMAND} -E rm -rf "${CMAKE_BINARY_DIR}/bin"
    COMMAND ${CMAKE_COMMAND} -E rename "${CMAKE_BINARY_DIR}/TagStudio_python" "${CMAKE_BINARY_DIR}/bin"
    COMMAND ${CMAKE_COMMAND} -E touch "${STAMP_DIR}/1"
    OUTPUT "${STAMP_DIR}/1")
add_custom_command(
    VERBATIM
    USES_TERMINAL
    DEPENDS "${STAMP_DIR}/1"
    WORKING_DIRECTORY "${CMAKE_BINARY_DIR}/bin/_internal"
    COMMAND ${CMAKE_COMMAND} -E tar xv "base_library.zip"
    COMMAND ${CMAKE_COMMAND} -E rm -r "base_library.zip"
    COMMAND ${CMAKE_COMMAND} -E touch "${STAMP_DIR}/2"
    OUTPUT "${STAMP_DIR}/2")
add_custom_target(TagStudio
    ALL
    DEPENDS "${STAMP_DIR}/2"
    SOURCES ${PYMODULE_SRC})
