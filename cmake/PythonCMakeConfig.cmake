# Inspired from: https://doc.qt.io/qtforpython-6/examples/example_scriptableapplication_scriptableapplication.html


function(__python_query_config resultVar option)
    list(POP_FRONT ARGV)
    execute_process(
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/cmake/python_cmake_config.py" ${ARGV}
        OUTPUT_VARIABLE ${resultVar}
        OUTPUT_STRIP_TRAILING_WHITESPACE
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        COMMAND_ECHO STDOUT
        COMMAND_ERROR_IS_FATAL ANY)

    return(PROPAGATE ${resultVar})
endfunction()

function(python_check_version)
    __python_query_config(__DISCARDED "pyproj" "version")
endfunction()

function(__python_get_dependencies resultVar)
    cmake_parse_arguments(PARSE_ARGV 1
        "arg"
        "DEV"
        "INCLUDE;EXCLUDE"
        "")

    set(__CACHE_VAR "__CMAKE_PYENV_DEPENDENCIES")
    if(arg_DEV)
        unset(arg_DEV)
        set(arg_DEV "dev")
        set(__CACHE_VAR "__CMAKE_PYENV_DEV_DEPENDENCIES")
    else()
        set(arg_DEV "")
    endif()

    if(DEFINED CACHE{${__CACHE_VAR}})
        set(${resultVar} ${${__CACHE_VAR}})
    else()
        __python_query_config(${resultVar} "pyproj" "${arg_DEV}deps")
        list(TRANSFORM ${resultVar} TOLOWER)
        set(${__CACHE_VAR} "${${resultVar}}" CACHE INTERNAL "")
    endif()

    if(DEFINED arg_INCLUDE)
        string(TOLOWER ${arg_INCLUDE} arg_INCLUDE)
        string(APPEND ${arg_INCLUDE} "*")
        list(FILTER ${resultVar} INCLUDE REGEX ${arg_INCLUDE})
    elseif(DEFINED arg_EXCLUDE)
        string(TOLOWER ${arg_EXCLUDE} arg_EXCLUDE)
        string(APPEND ${arg_EXCLUDE} "*")
        list(FILTER ${resultVar} EXCLUDE REGEX ${arg_EXCLUDE})
    endif()
    
    list(LENGTH ${resultVar} __LIST_LENGTH)
    if(NOT __LIST_LENGTH GREATER_EQUAL 1)
        message(FATAL_ERROR "Error while parsing project's requirements")
    endif()

    return(PROPAGATE ${resultVar})
endfunction()

function(python_get_dependencies resultVar)
    list(POP_FRONT ARGV)
    __python_get_dependencies(${resultVar} ${ARGV})
    return(PROPAGATE ${resultVar})
endfunction()

function(python_get_dev_dependencies resultVar)
    list(POP_FRONT ARGV)
    __python_get_dependencies(${resultVar} "DEV" ${ARGV})
    return(PROPAGATE ${resultVar})
endfunction()

function(python_pip_install)
    execute_process(
        COMMAND "${Python3_EXECUTABLE}" -m pip install ${ARGV}
        COMMAND_ECHO STDOUT
        COMMAND_ERROR_IS_FATAL ANY)
endfunction()

function(python_create_venv envpath)
    execute_process(
        COMMAND "${Python3_EXECUTABLE}" -m venv "${envpath}" --copies
        COMMAND_ECHO STDOUT
        COMMAND_ERROR_IS_FATAL ANY)
endfunction()


macro(module_target nicename module)
    __python_query_config(MODULE_PATH_${nicename} "module" "${module}")
    list(TRANSFORM MODULE_PATH_${nicename} REPLACE "\\\\" "/")

    set(MODULE_NAME_${nicename} "${module}")
endmacro()

function(__module_sanity_check nicename)
    if(NOT DEFINED MODULE_PATH_${nicename} OR NOT DEFINED MODULE_NAME_${nicename})
        message(FATAL_ERROR "\"module_target\" must be called first before using any other \"module_*\" macros.")
    endif()
endfunction()

macro(module_library nicename library)
    __module_sanity_check(${nicename})

    message(CHECK_START "Looking for library '${library}' in module '${MODULE_NAME_${nicename}}'")
    find_library(${nicename}_LIBRARIES "${library}.abi3"
        PATHS ${MODULE_PATH_${nicename}}
        NO_DEFAULT_PATH)
    if(NOT ${nicename}_LIBRARIES)
        message(CHECK_FAIL "not found.")
        message(FATAL_ERROR "'${MODULE_NAME_${nicename}}': '${library}' library not found.")
    endif()
    message(CHECK_PASS "found.")

    add_library(${nicename}Lib SHARED IMPORTED)
    set(LIB_PROP IMPORTED_LOCATION)
    if(WIN32)
        list(
            TRANSFORM ${nicename}_LIBRARIES
            REPLACE "^(.*)\\.lib$" "\\1.dll"
            OUTPUT_VARIABLE ${nicename}_DLLS)
        set_target_properties(${nicename}Lib PROPERTIES IMPORTED_LOCATION ${${nicename}_DLLS})
        set(LIB_PROP IMPORTED_IMPLIB)
    endif()
    set_target_properties(${nicename}Lib PROPERTIES ${LIB_PROP} ${${nicename}_LIBRARIES})
endmacro()

macro(module_program nicename executable)
    __module_sanity_check(${nicename})

    message(CHECK_START "Looking for executable '${executable}' in module '${MODULE_NAME_${nicename}}'")
    find_program(${nicename}_EXECUTABLE "${executable}"
        PATHS ${MODULE_PATH_${nicename}}
        NO_DEFAULT_PATH)
    if(NOT ${nicename}_EXECUTABLE)
        message(CHECK_FAIL "not found.")
        message(FATAL_ERROR "'${MODULE_NAME_${nicename}}': '${executable}' executable not found.")
    endif()
    message(CHECK_PASS "found.")

    add_executable(${nicename}Exe IMPORTED)
    set_target_properties(${nicename}Exe
        PROPERTIES
            IMPORTED_LOCATION ${${nicename}_EXECUTABLE})
endmacro()

macro(module_directory nicename dir)
    __module_sanity_check(${nicename})

    string(TOUPPER "${dir}" dirvar)
    set(${nicename}_${dirvar}_DIR "${MODULE_PATH_${nicename}}/${dir}")

    message(CHECK_START "Looking for directory '${dir}' in module '${MODULE_NAME_${nicename}}'")
    if(NOT EXISTS ${${nicename}_${dirvar}_DIR} OR NOT IS_DIRECTORY ${${nicename}_${dirvar}_DIR})
        message(CHECK_FAIL "not found.")
        message(FATAL_ERROR "'${MODULE_NAME_${nicename}}': '${dir}' directory not found.")
    endif()
    message(CHECK_PASS "found.")
endmacro()
