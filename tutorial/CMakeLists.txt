cmake_minimum_required(VERSION 3.20)
project(MLIRSummerSchool2026CIRCT LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17 CACHE STRING "C++ standard")
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(CIRCT REQUIRED CONFIG)

message(STATUS "Using CIRCTConfig.cmake in: ${CIRCT_DIR}")
message(STATUS "Using MLIRConfig.cmake in: ${MLIR_DIR}")
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")

set(LLVM_RUNTIME_OUTPUT_INTDIR ${CMAKE_BINARY_DIR}/bin)
set(LLVM_LIBRARY_OUTPUT_INTDIR ${CMAKE_BINARY_DIR}/lib)
set(MLIR_BINARY_DIR ${CMAKE_BINARY_DIR})

list(APPEND CMAKE_MODULE_PATH
  "${CIRCT_CMAKE_DIR}"
  "${MLIR_CMAKE_DIR}"
  "${LLVM_CMAKE_DIR}"
)

include(TableGen)
include(AddLLVM)
include(AddMLIR)
include(AddCIRCT)
include(HandleLLVMOptions)

include_directories(SYSTEM ${LLVM_INCLUDE_DIRS})
include_directories(SYSTEM ${MLIR_INCLUDE_DIRS})
include_directories(SYSTEM ${CIRCT_INCLUDE_DIRS})
include_directories(${PROJECT_SOURCE_DIR}/include)

link_directories(${LLVM_LIBRARY_DIRS})
link_directories(${CIRCT_LIBRARY_DIRS})

add_subdirectory(lib)
add_subdirectory(tools/circt-tutorial-opt)
