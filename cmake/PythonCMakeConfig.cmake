# Inspired from: https://doc.qt.io/qtforpython-6/examples/example_scriptableapplication_scriptableapplication.html


function(python_query_config resultVar option)
    list(POP_FRONT ARGV)
    execute_process(
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/cmake/python_cmake_config.py" ${ARGV}
        OUTPUT_VARIABLE ${resultVar}
        OUTPUT_STRIP_TRAILING_WHITESPACE
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        COMMAND_ECHO STDOUT
        COMMAND_ERROR_IS_FATAL ANY)

    list(TRANSFORM ${resultVar} REPLACE "\\\\" "/")
    return(PROPAGATE ${resultVar})
endfunction()

function(python_pip_install)
    execute_process(
        COMMAND "${Python3_EXECUTABLE}" -m pip install ${ARGV}
        COMMAND_ECHO STDOUT
        COMMAND_ERROR_IS_FATAL ANY)
endfunction()


macro(module_target nicename module)
    python_query_config(MODULE_PATH_${nicename} "module" "${module}")

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

macro(module_include nicename)
    __module_sanity_check(${nicename})

    set(${nicename}_INCLUDE_DIR "${MODULE_PATH_${nicename}}/include")

    message(CHECK_START "Looking for include directory in module '${MODULE_NAME_${nicename}}'")
    if(NOT EXISTS ${${nicename}_INCLUDE_DIR} OR NOT IS_DIRECTORY ${${nicename}_INCLUDE_DIR})
        message(CHECK_FAIL "not found.")
        message(FATAL_ERROR "'${MODULE_NAME_${nicename}}': include directory not found.")
    endif()
    message(CHECK_PASS "found.")
endmacro()
