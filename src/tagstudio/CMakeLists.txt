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
list(APPEND PYMODULE_SRC "${CMAKE_SOURCE_DIR}/tagstudio.spec")
set(STAMP_DIR "${CMAKE_CURRENT_BINARY_DIR}/pymodule_stamp")
# Note: PyInstaller seems to be unable to handle a debug Python.
add_custom_command(
    VERBATIM
    USES_TERMINAL
    DEPENDS ${PYMODULE_SRC}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMAND ${CMAKE_COMMAND} -E touch "${CMAKE_CURRENT_SOURCE_DIR}/main.py"
    COMMAND Python3::InterpreterMultiConfig
    "-m" "PyInstaller" "${CMAKE_SOURCE_DIR}/tagstudio.spec"
    "--distpath" "${CMAKE_CURRENT_BINARY_DIR}/dist"
    "--workpath" ${CMAKE_CURRENT_BINARY_DIR}
    "-y" "--" "--cppready"
    COMMAND ${CMAKE_COMMAND} -E rm -rf "${CMAKE_BINARY_DIR}/bin/_internal"
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${CMAKE_CURRENT_BINARY_DIR}/dist/TagStudio" "${CMAKE_BINARY_DIR}/bin"
    COMMAND ${CMAKE_COMMAND} -E touch "${STAMP_DIR}/1"
    OUTPUT "${STAMP_DIR}/1")
if (WIN32)
    list(APPEND DLL_COMMAND_1
        "-D" "GLOBEX=${CMAKE_BINARY_DIR}/bin/_internal/*.dll"
        "-D" "DIR=${CMAKE_BINARY_DIR}/bin/"
        "-P" "${CMAKE_SOURCE_DIR}/cmake/GlobMove.cmake")
    # Make an exception for the non-stable-interface module as the PyInstaller
    # executable needs it and explicitly looks for it on startup.
    list(APPEND DLL_COMMAND_2
        -E copy
        "${CMAKE_BINARY_DIR}/bin/$<TARGET_FILE_NAME:Python3::Module>"
        "${CMAKE_BINARY_DIR}/bin/_internal")
else()
    list(APPEND DLL_COMMAND_1 "-E" "true")
    list(APPEND DLL_COMMAND_2 "-E" "true")
endif()
add_custom_command(
    VERBATIM
    USES_TERMINAL
    DEPENDS "${STAMP_DIR}/1"
    WORKING_DIRECTORY "${CMAKE_BINARY_DIR}/bin/_internal"
    COMMAND ${CMAKE_COMMAND} -E tar xv "base_library.zip"
    COMMAND ${CMAKE_COMMAND} -E rm -r "base_library.zip"
    COMMAND ${CMAKE_COMMAND} ${DLL_COMMAND_1}
    COMMAND ${CMAKE_COMMAND} ${DLL_COMMAND_2}
    COMMAND ${CMAKE_COMMAND} -E touch "${STAMP_DIR}/2"
    OUTPUT "${STAMP_DIR}/2")
add_custom_target(TagStudio
    ALL
    DEPENDS "${STAMP_DIR}/2"
    SOURCES ${PYMODULE_SRC})
