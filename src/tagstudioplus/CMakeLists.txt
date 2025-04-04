project(TagStudioPlus)


file(GLOB_RECURSE TSPLUS_SRC
    CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/*.h"
    "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp")

add_executable(${PROJECT_NAME} ${TSPLUS_SRC})
add_dependencies(${PROJECT_NAME} TagStudio)
target_link_libraries(${PROJECT_NAME} PRIVATE Python3::Module)
set_target_properties(${PROJECT_NAME}
    PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
