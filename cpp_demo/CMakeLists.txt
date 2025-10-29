cmake_minimum_required(VERSION 3.10)
project(MocapApiDemo)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 设置包含目录
include_directories(${CMAKE_SOURCE_DIR}/include)

# 添加源文件
add_executable(MocapApiDemo src/main.cpp)

# MocapApi库文件路径
set(MOCAP_API_LIB_DIR "${CMAKE_SOURCE_DIR}/../MocapApi/mocap_api/lib/amd64")

# 链接库
target_link_libraries(MocapApiDemo
    PRIVATE
    ${MOCAP_API_LIB_DIR}/MocapApi.lib
    winmm.lib
)

# 复制DLL文件到输出目录
add_custom_command(TARGET MocapApiDemo POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
    ${MOCAP_API_LIB_DIR}/MocapApi.dll
    $<TARGET_FILE_DIR:MocapApiDemo>
)

# 设置输出目录
set_target_properties(MocapApiDemo PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)
