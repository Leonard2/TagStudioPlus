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

    return(PROPAGATE ${resultVar})
endfunction()

function(python_pip_install)
    execute_process(
        COMMAND "${Python3_EXECUTABLE}" -m pip install ${ARGV}
        COMMAND_ECHO STDOUT
        COMMAND_ERROR_IS_FATAL ANY)
endfunction()
