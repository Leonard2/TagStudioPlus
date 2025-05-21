project(TagStudio)

include(${CMAKE_SOURCE_DIR}/cmake/PythonCMakeConfig.cmake)


# Install modules necessary for running the python app.
python_query_config(CMAKE_PYENV_DEPENDENCIES "pyproj" "deps")
# We need to remove this entry to avoid conflicting with self-built PySide (if used).
list(FILTER CMAKE_PYENV_DEPENDENCIES EXCLUDE REGEX "PySide6*")
python_pip_install(${CMAKE_PYENV_DEPENDENCIES})
# Install development python modules.
if (NOT DEFINED NO_PYTHON_DEVTOOLS)
    python_query_config(CMAKE_PYENV_DEV_DEPENDENCIES "pyproj" "devdeps")
    python_pip_install(${CMAKE_PYENV_DEV_DEPENDENCIES})
endif()

file(GLOB_RECURSE PYMODULE_SRC CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/*")
list(APPEND PYMODULE_SRC "${CMAKE_SOURCE_DIR}/tagstudio.spec")
set(STAMP_FILE "${CMAKE_CURRENT_BINARY_DIR}/pymodule.stamp")
# Note: PyInstaller seems to be unable to handle a debug Python.
add_custom_command(
    VERBATIM
    USES_TERMINAL
    DEPENDS ${PYMODULE_SRC}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Building Python module with PyInstaller."
    COMMAND ${CMAKE_COMMAND} -E touch "${CMAKE_CURRENT_SOURCE_DIR}/main.py"
    COMMAND Python3::InterpreterMultiConfig
    "-m" "PyInstaller" "${CMAKE_SOURCE_DIR}/tagstudio.spec"
    "--distpath" "${CMAKE_CURRENT_BINARY_DIR}/dist"
    "--workpath" ${CMAKE_CURRENT_BINARY_DIR}
    "-y" "--" "--cppready"
    COMMAND ${CMAKE_COMMAND} -E rm -rf "${CMAKE_BINARY_DIR}/bin/_internal"
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${CMAKE_CURRENT_BINARY_DIR}/dist/TagStudio" "${CMAKE_BINARY_DIR}/bin"
    COMMAND ${CMAKE_COMMAND} -E touch ${STAMP_FILE}
    OUTPUT ${STAMP_FILE})
add_custom_target(TagStudio
    ALL
    DEPENDS ${STAMP_FILE}
    SOURCES ${PYMODULE_SRC})
