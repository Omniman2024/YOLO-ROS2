cmake_minimum_required(VERSION 3.8)
project(conveyor_belt)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(gz-plugin2 REQUIRED COMPONENTS register)
find_package(gz-sim8 REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(robot_state_publisher REQUIRED)
find_package(xacro REQUIRED)
find_package(ros_gz_sim REQUIRED)
find_package(ros_gz_bridge REQUIRED)

add_library(conveyor_belt_plugin SHARED
    src/conveyor_belt_plugin.cpp
)

target_include_directories(conveyor_belt_plugin PRIVATE
    include
)

target_link_libraries(conveyor_belt_plugin
    gz-plugin2::gz-plugin2-register
    gz-sim8::gz-sim8
)

install(DIRECTORY
    include
    urdf
    meshes
    launch
    worlds
    scripts
    DESTINATION share/${PROJECT_NAME}/
)

install(
    PROGRAMS
    scripts/spawn_object.py
    scripts/spawn_sequence.py
    scripts/spawn_static_model.py
    scripts/conveyor_relay.py
    DESTINATION lib/${PROJECT_NAME}
)

install(
    TARGETS conveyor_belt_plugin
    LIBRARY DESTINATION lib
)

ament_package()
