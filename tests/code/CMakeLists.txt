cmake_minimum_required(VERSION 3.14)

project(sclang_code_unittest)

find_package(Python3 COMPONENTS Interpreter REQUIRED)

set(sclang_root ${CMAKE_CURRENT_SOURCE_DIR}/../..)

function (add_test name)
    add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${name}.h ${CMAKE_CURRENT_BINARY_DIR}/${name}.c
                    COMMAND ${Python3_EXECUTABLE} -m sclang.tools.code -o ${CMAKE_CURRENT_BINARY_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/${name}.sc
                    WORKING_DIRECTORY ${sclang_root}
                    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/${name}.sc)

    add_executable(test_${name} test_${name}.c ${CMAKE_CURRENT_BINARY_DIR}/${name}.c)
    target_include_directories(test_${name} PRIVATE ${CMAKE_CURRENT_BINARY_DIR} ${CMAKE_CURRENT_SOURCE_DIR})
endfunction()

add_test(simplest)
add_test(guard)
add_test(actions)
add_test(internal_transition)
