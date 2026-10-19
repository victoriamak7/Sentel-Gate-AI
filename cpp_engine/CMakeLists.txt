cmake_minimum_required(VERSION 3.20)
project(sentinel_cpp_scanner LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(include)

# Check for pybind11
find_package(pybind11 CONFIG QUIET)

if(pybind11_FOUND)
    pybind11_add_module(sentinel_cpp_scanner 
        src/sentinel_scanner.cpp 
        src/bindings.cpp
    )
    target_include_directories(sentinel_cpp_scanner PRIVATE include)
else()
    message(STATUS "pybind11 not found globally. Building standalone static/shared library.")
    add_library(sentinel_cpp_scanner SHARED
        src/sentinel_scanner.cpp
    )
    target_include_directories(sentinel_cpp_scanner PUBLIC include)
endif()
