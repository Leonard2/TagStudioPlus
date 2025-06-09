project(TagStudioPlus)


set(QT_COMPONENTS Core Gui Widgets)

# Get the Shiboken generator as a target.
module_target(ShibokenGen "shiboken6_generator")
module_program(ShibokenGen "shiboken6")
module_directory(ShibokenGen "include") # Needed for the imported library target.

# Get the PySide module as a target.
module_target(PySide "PySide6")
module_library(PySide "pyside6")
module_directory(PySide "include")
module_directory(PySide "typesystems")
set_target_properties(PySideLib
    PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES ${PySide_INCLUDE_DIR})

# Generate Shiboken binding files.
function(genex_escape var)
    # https://discourse.cmake.org/t/mapping-lists-in-generator-expressions/12833/3
    # Non-recursive
    string(REPLACE "\\<"            "<"             ${var} "${${var}}")
    string(REPLACE "\\>"            "__ANGLE_R__"   ${var} "${${var}}")
    string(REPLACE "\\$"            "$<1:$>"        ${var} "${${var}}")
    string(REPLACE "\\,"            "$<COMMA>"      ${var} "${${var}}")
    string(REPLACE "__ANGLE_R__"    "$<ANGLE-R>"    ${var} "${${var}}")

    return(PROPAGATE ${var})
endfunction()

string(
    APPEND GENEX_BINDINGS_INCLUDE
    "$<LIST:REMOVE_DUPLICATES,"
        "$<GENEX_EVAL:"
            "$<LIST:TRANSFORM,"
                "${QT_COMPONENTS},"
                "REPLACE,"
                "(.+),"
                "\\$\\<TARGET_PROPERTY:"
                    "Qt6::\\1\\,"
                    "INTERFACE_INCLUDE_DIRECTORIES"
                "\\>"
            ">"
        ">"
    ">")
genex_escape(GENEX_BINDINGS_INCLUDE)

set(BINDINGS_INPUT
    "${CMAKE_CURRENT_SOURCE_DIR}/application.h")
set(BINDINGS_OUTDIR "${CMAKE_CURRENT_BINARY_DIR}/bindings")
set(BINDINGS_OUTPUT
    "${BINDINGS_OUTDIR}/tagstudioplus/tagstudioplus_module_wrapper.cpp"
    "${BINDINGS_OUTDIR}/tagstudioplus/tspapplication_wrapper.cpp")
add_custom_command(
    COMMENT "Running Shiboken generator on bindings."
    COMMAND_EXPAND_LISTS
    DEPENDS
        "${CMAKE_CURRENT_SOURCE_DIR}/bindings.xml"
        ${BINDINGS_INPUT}
    COMMAND ShibokenGenExe
        "--generator-set=shiboken"
        "--avoid-protected-hack"
        "--enable-parent-ctor-heuristic"
        "--use-global-header"
        "--enable-pyside-extensions"
        "--output-directory=${BINDINGS_OUTDIR}"
        "-T${PySide_TYPESYSTEMS_DIR}"
        "-T${CMAKE_CURRENT_SOURCE_DIR}"
        "$<LIST:TRANSFORM,${GENEX_BINDINGS_INCLUDE},PREPEND,-I>"
        "-I${CMAKE_CURRENT_SOURCE_DIR}"
        ${BINDINGS_INPUT}
        "${CMAKE_CURRENT_SOURCE_DIR}/bindings.xml"
    OUTPUT ${BINDINGS_OUTPUT})

# Get Shiboken library as a target.
module_target(Shiboken "shiboken6")
module_library(Shiboken "shiboken6")
set_target_properties(ShibokenLib
    PROPERTIES
        # As of 6.8.2.1, Shiboken uses a Python 3.8.0 limited API.
        INTERFACE_COMPILE_DEFINITIONS "Py_LIMITED_API=0x03080000"
        INTERFACE_INCLUDE_DIRECTORIES ${ShibokenGen_INCLUDE_DIR})
target_link_libraries(ShibokenLib INTERFACE Python3::SABIModule)

# Create our bindings target.
set(BINDLIBTYPE "STATIC")
if(BUILD_SHARED_LIBS)
    set(BINDLIBTYPE "MODULE")
endif()
add_library(TagStudioPlusBindings ${BINDLIBTYPE} ${BINDINGS_OUTPUT})
target_link_libraries(TagStudioPlusBindings
    PUBLIC
        ShibokenLib
        PySideLib)
target_include_directories(TagStudioPlusBindings
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
    PUBLIC
        "${BINDINGS_OUTDIR}/tagstudioplus")
foreach(COMPONENT ${QT_COMPONENTS})
    target_link_libraries(TagStudioPlusBindings
        PUBLIC Qt6::${COMPONENT})
    target_include_directories(TagStudioPlusBindings
        PUBLIC "${PySide_INCLUDE_DIR}/Qt${COMPONENT}")
endforeach()

# Main executable.
# Note: this must be the same version of Qt used to build PySide.
# They should really add a way to query this information from the module.
find_package(Qt6 REQUIRED COMPONENTS ${QT_COMPONENTS})

file(GLOB_RECURSE TSPLUS_SRC
    CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/*.h"
    "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp")

qt_add_executable(${PROJECT_NAME} ${TSPLUS_SRC})
add_dependencies(${PROJECT_NAME} TagStudio)
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(${PROJECT_NAME}
    PRIVATE
        ShibokenLib
        TagStudioPlusBindings)
set_target_properties(${PROJECT_NAME}
    PROPERTIES
        AUTOMOC ON
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

if (WIN32)
    string(
        APPEND GENEX_DLLS
        "$<JOIN:"
            "$<LIST:TRANSFORM,"
                "$<LIST:REMOVE_ITEM,"
                    "$<PATH:GET_FILENAME,"
                        "$<TARGET_RUNTIME_DLLS:${PROJECT_NAME}>"
                    ">,"
                    # Make an exception for the non-stable-interface module as the PyInstaller
                    # executable needs it and explicitly looks for it on startup.
                    "$<TARGET_FILE_NAME:Python3::Module>"
                ">,"
                "PREPEND,"
                "${CMAKE_BINARY_DIR}/bin/_internal/*"
            ">,"
            "\\;"
        ">")

    add_custom_command(TARGET ${PROJECT_NAME}
        POST_BUILD
        VERBATIM
        USES_TERMINAL
        COMMAND_EXPAND_LISTS
        # https://gitlab.kitware.com/cmake/cmake/-/issues/15461
        COMMENT "Copying DLL files to bin folder."
        COMMAND ${CMAKE_COMMAND}
            -E copy
            $<TARGET_RUNTIME_DLLS:${PROJECT_NAME}>
            $<TARGET_FILE_DIR:${PROJECT_NAME}>
        # Remove DLLs that are now duplicated inside the directory generated by PyInstaller.
        COMMAND ${CMAKE_COMMAND}
            -D "GLOBEX=${GENEX_DLLS}"
            -P "${CMAKE_SOURCE_DIR}/cmake/GlobRemove.cmake")
endif()
