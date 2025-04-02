cmake_minimum_required(VERSION 3.30)

project(TagStudioPlusPlus LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


#[
# Create a Python virutal environment.
set(CMAKE_PYENV "${CMAKE_CURRENT_SOURCE_DIR}/python_env")
add_subdirectory(${CMAKE_PYENV})
set(ENV{VIRTUAL_ENV} "${CMAKE_PYENV}")
set(Python3_FIND_VIRTUALENV FIRST)

# Note: for now -DPython3_SABI_LIBRARY seems to UTTERLY fail on windows.
# TODO: Look into it, because the stable ABI is obviously the better option.
set(Python3_EXECUTABLE "")
find_package(Python3 3.12 REQUIRED COMPONENTS Interpreter Development)

# Install base Python modules (PySide is needed to configure CMake).
execute_process(
    COMMAND "${Python3_EXECUTABLE}" -m pip install setuptools packaging Pyinstaller==6.6.0 cmakelang
    COMMAND_ERROR_IS_FATAL ANY)
if(NOT DEFINED PYSIDE_WHEELS)
    # For self-built PySide6, you may use the "create_wheels.py" script to create packages.
    # Set "PYSIDE_WHEELS" to the directory containing the generated wheels to re-use them.
    # As of 28/03/25, PySide is prebuilt for Python 3.9 in pip and TagStudio supports only
    # Python 3.12 minimum, so this is most likely needed.
    set(PYSIDE_WHEELS "PySide6==6.8.0.1")
else()
    file(GLOB PYSIDE_WHEELS "${PYSIDE_WHEELS}/*.whl")
endif()
execute_process(
    COMMAND "${Python3_EXECUTABLE}" -m pip install ${PYSIDE_WHEELS}
    COMMAND_ERROR_IS_FATAL ANY)
#]


add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/src/tagstudio")
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/src/tagstudioplus")
