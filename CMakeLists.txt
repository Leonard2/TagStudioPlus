cmake_minimum_required(VERSION 3.30)

project(TagStudioPlus LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Only static supported for now.
set(BUILD_SHARED_LIBS OFF)


#[
include(${CMAKE_SOURCE_DIR}/cmake/PythonCMakeConfig.cmake)

# Create a Python virutal environment.
set(CMAKE_PYENV "${CMAKE_CURRENT_SOURCE_DIR}/python_env")
add_subdirectory(${CMAKE_PYENV})
set(ENV{VIRTUAL_ENV} "${CMAKE_PYENV}")
set(Python3_FIND_VIRTUALENV ONLY)

set(Python3_EXECUTABLE "")
set(Python3_ROOT_DIR "")
find_package(Python3 REQUIRED COMPONENTS Interpreter)

# Install base Python modules (mostly needed to run the Python configuration script).
python_pip_install(setuptools packaging cmakelang)
# We only check for the version now because the script needs the 'packaging' module to work.
python_check_version()
# PyInstaller is not strictly needed during generation/configuration but will be needed at build time.
python_get_dev_dependencies(__PYINSTALLER INCLUDE "PyInstaller")
python_pip_install("${__PYINSTALLER}")

# We take care of PySide right now because it will be needed to configure the project later on.
if(NOT DEFINED PYSIDE_WHEELS)
    # Query the PySide requirement from the pyproject config.
    python_get_dependencies(PYSIDE_WHEELS INCLUDE "PySide6")
else()
    # For self-built PySide6, you may use the "create_wheels.py" script to create packages.
    # Set "PYSIDE_WHEELS" to the directory containing the generated wheels to re-use them.
    # As of 28/03/25, PySide is prebuilt for Python 3.9 in pip and TagStudio supports only
    # Python 3.12 minimum, so this is most likely needed.
    file(GLOB PYSIDE_WHEELS "${PYSIDE_WHEELS}/*.whl")
endif()
python_pip_install(${PYSIDE_WHEELS})
#]


add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/src/tagstudio")
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/src/tagstudioplus")
