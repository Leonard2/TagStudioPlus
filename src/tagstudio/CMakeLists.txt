project(TagStudio)


# Install modules necessary for running the python app.
# We need to remove the PySide entry to avoid conflicting with the self-built wheels (if used).
python_get_dependencies(PYENV_DEPENDENCIES EXCLUDE "PySide6")
python_pip_install(${PYENV_DEPENDENCIES})
# Install development python modules.
if (NOT DEFINED NO_PYTHON_DEVTOOLS)
    python_get_dev_dependencies(PYENV_DEV_DEPENDENCIES)
    python_pip_install(${PYENV_DEV_DEPENDENCIES})
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
