cmake_minimum_required(VERSION 3.15)

project(MocapApiDemo)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 设置MocapApi的头文件路径
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/MocapApi/mocap_api/include/MocapApi)

# 添加可执行文件
add_executable(mocap_demo main.cpp)

# 根据平台链接相应的库
if(WIN32)
    # Windows平台
    target_link_libraries(mocap_demo ${CMAKE_CURRENT_SOURCE_DIR}/MocapApi/mocap_api/lib/amd64/MocapApi.lib)
    # 将DLL文件复制到输出目录
    add_custom_command(
        TARGET mocap_demo POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_CURRENT_SOURCE_DIR}/MocapApi/mocap_api/lib/amd64/MocapApi.dll
        $<TARGET_FILE_DIR:mocap_demo>
    )
elseif(UNIX AND NOT APPLE)
    # Linux平台
    if(CMAKE_SYSTEM_PROCESSOR STREQUAL "aarch64")
        target_link_libraries(mocap_demo ${CMAKE_CURRENT_SOURCE_DIR}/MocapApi/mocap_api/lib/arm64/libMocapApi.so)
    else()
        target_link_libraries(mocap_demo ${CMAKE_CURRENT_SOURCE_DIR}/MocapApi/mocap_api/lib/x86_64/libMocapApi.so)
    endif()
endif()