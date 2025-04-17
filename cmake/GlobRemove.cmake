foreach(EXPR ${GLOBEX})
    file(GLOB_RECURSE RESULTS ${EXPR})
endforeach()
file(REMOVE ${RESULTS})
