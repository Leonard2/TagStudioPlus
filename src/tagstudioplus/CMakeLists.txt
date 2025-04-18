project(TagStudioPlus)

include(${CMAKE_SOURCE_DIR}/cmake/PythonCMakeConfig.cmake)


# Get the Shiboken generator as a target.
python_query_config(SHIBOKEN_EXECUTABLE "--shiboken-generator")
add_executable(ShibokenGen IMPORTED)
set_target_properties(ShibokenGen
    PROPERTIES
        IMPORTED_LOCATION ${SHIBOKEN_EXECUTABLE})

# Generate Shiboken binding files.
set(BINDINGS_INPUT
    "${CMAKE_CURRENT_SOURCE_DIR}/cppswitch.h")
set(BINDINGS_OUTDIR "${CMAKE_CURRENT_BINARY_DIR}/bindings")
set(BINDINGS_OUTPUT
    "${BINDINGS_OUTDIR}/tagstudioplus/tagstudioplus_module_wrapper.cpp"
    "${BINDINGS_OUTDIR}/tagstudioplus/cppswitch_wrapper.cpp")
add_custom_command(
    COMMENT "Running Shiboken generator on bindings."
    DEPENDS
        "${CMAKE_CURRENT_SOURCE_DIR}/bindings.xml"
        ${BINDINGS_INPUT}
    COMMAND ShibokenGen
        "--generator-set=shiboken"
        "--avoid-protected-hack"
        "--use-global-header"
        "--output-directory=${BINDINGS_OUTDIR}"
        "-T${CMAKE_CURRENT_SOURCE_DIR}"
        "-I${CMAKE_CURRENT_SOURCE_DIR}"
        ${BINDINGS_INPUT}
        "${CMAKE_CURRENT_SOURCE_DIR}/bindings.xml"
    OUTPUT ${BINDINGS_OUTPUT})

# Get Shiboken library as a target.
python_query_config(SHIBOKEN_INCLUDE_DIR "--shiboken-include")
python_query_config(SHIBOKEN_LIBRARIES "--shiboken-library")
add_library(ShibokenLib SHARED IMPORTED)
set_target_properties(ShibokenLib
    PROPERTIES
        IMPORTED_LOCATION ${SHIBOKEN_LIBRARIES}
        INTERFACE_INCLUDE_DIRECTORIES ${SHIBOKEN_INCLUDE_DIR})
if(WIN32)
    list(TRANSFORM SHIBOKEN_LIBRARIES REPLACE "^(.*)\\.dll$" "\\1.lib")
    set_target_properties(ShibokenLib PROPERTIES IMPORTED_IMPLIB ${SHIBOKEN_LIBRARIES})
endif()
# TODO: Should really be the SABI Module.
target_link_libraries(ShibokenLib INTERFACE Python3::Module)

# Create our bindings target.
set(BINDLIBTYPE "STATIC")
if(BUILD_SHARED_LIBS)
    set(BINDLIBTYPE "MODULE")
endif()
add_library(TagStudioPlusBindings ${BINDLIBTYPE} ${BINDINGS_OUTPUT})
target_link_libraries(TagStudioPlusBindings PUBLIC ShibokenLib)
target_include_directories(TagStudioPlusBindings
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
    PUBLIC
        "${BINDINGS_OUTDIR}/tagstudioplus")

# Main executable.
file(GLOB_RECURSE TSPLUS_SRC
    CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/*.h"
    "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp")

add_executable(${PROJECT_NAME} ${TSPLUS_SRC})
add_dependencies(${PROJECT_NAME} TagStudio)
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(${PROJECT_NAME}
    PRIVATE
        ShibokenLib
        TagStudioPlusBindings)
set_target_properties(${PROJECT_NAME}
    PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
