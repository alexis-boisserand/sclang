cmake_minimum_required(VERSION 3.14)

project(scgen_code_unittest)

find_package(Python3 COMPONENTS Interpreter REQUIRED)

set(scgen_root ${CMAKE_CURRENT_SOURCE_DIR}/../..)
set(test_models_dir ${scgen_root}/tests/models)

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/simplest.h ${CMAKE_CURRENT_BINARY_DIR}/simplest.c
                   COMMAND ${Python3_EXECUTABLE} -m scgen.code -o ${CMAKE_CURRENT_BINARY_DIR} -sc ${test_models_dir}/simplest.yaml
                   WORKING_DIRECTORY ${scgen_root}
                   DEPENDS ${test_models_dir}/simplest.yaml)

add_executable(test_simplest test_simplest.c ${CMAKE_CURRENT_BINARY_DIR}/simplest.c)

target_compile_definitions(test_simplest PRIVATE UNIT_TEST)
target_include_directories(test_simplest PRIVATE ${CMAKE_CURRENT_BINARY_DIR})