cmake_minimum_required(VERSION 3.14)

project(sclang_code_unittest)

find_package(Python3 COMPONENTS Interpreter REQUIRED)

set(sclang_root ${CMAKE_CURRENT_SOURCE_DIR}/../..)

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/simplest.hc ${CMAKE_CURRENT_BINARY_DIR}/simplest.c
                   COMMAND ${Python3_EXECUTABLE} -m sclang.tools.code -o ${CMAKE_CURRENT_BINARY_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/simplest.sc
                   WORKING_DIRECTORY ${sclang_root}
                   DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/simplest.sc)

add_executable(test_simplest test_simplest.c ${CMAKE_CURRENT_BINARY_DIR}/simplest.c)
target_include_directories(test_simplest PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
