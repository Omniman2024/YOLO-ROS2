#!/usr/bin/env python3
import os
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    pkg_conveyor = get_package_share_directory('conveyor_belt')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Fix mesh resolution: tell Gazebo where to find model://conveyor_belt/...
    set_gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=os.path.dirname(pkg_conveyor)
    )

    set_gz_plugin_path = SetEnvironmentVariable(
        name='GZ_SIM_SYSTEM_PLUGIN_PATH',
        value=os.path.join(os.path.dirname(pkg_conveyor), '..', 'lib')
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='Use simulation (Gazebo) clock'
    )
    use_sim_time = LaunchConfiguration('use_sim_time')

    world_file = os.path.join(pkg_conveyor, 'worlds', 'conveyor_world.sdf')

    xacro_file = os.path.join(pkg_conveyor, 'urdf', 'conveyor_belt.urdf.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': f'-r {world_file}',
            'on_exit_shutdown': 'true',
        }.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': robot_description,
        }],
    )

    spawn_conveyor = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_conveyor_belt',
        output='screen',
        arguments=[
            '-name', 'conveyor_belt',
            '-topic', '/robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.8',
        ],
    )

    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        output='screen',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/model/conveyor_belt/joint/belt_joint/cmd_vel@std_msgs/msg/Float64]gz.msgs.Double',
            '/model/conveyor_belt_2/joint/belt_joint/cmd_vel@std_msgs/msg/Float64]gz.msgs.Double',
            '/model/conveyor_belt/joint/spawn_pusher_joint/cmd_vel@std_msgs/msg/Float64]gz.msgs.Double',
            '/belt_camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/belt_camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
        ],
        parameters=[{'use_sim_time': use_sim_time}],
    )

    conveyor_relay = Node(
        package='conveyor_belt',
        executable='conveyor_relay.py',
        name='conveyor_relay',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )

    spawn_scanner = Node(
        package='conveyor_belt',
        executable='spawn_static_model.py',
        name='spawn_scanner',
        output='screen',
        arguments=[
            '--model', 'scanner.urdf.xacro',
            '--name', 'scanner',
            '--x', '0.0',
            '--y', '0.01',
            '--z', '0.0',
        ],
    )

    spawn_storage = Node(
        package='conveyor_belt',
        executable='spawn_static_model.py',
        name='spawn_storage',
        output='screen',
        arguments=[
            '--model', 'storage.urdf.xacro',
            '--name', 'storage',
            '--x', '10.0',
            '--y', '-0.1',
            '--z', '0.2',
        ],
    )

    spawn_ramp = Node(
        package='conveyor_belt',
        executable='spawn_static_model.py',
        name='spawn_ramp',
        output='screen',
        arguments=[
            '--model', 'ramp.urdf.xacro',
            '--name', 'ramp',
            '--x', '0.0',
            '--y', '0.01',
            '--z', '0.2',
        ],
    )

    spawn_piston_holder = Node(
        package='conveyor_belt',
        executable='spawn_static_model.py',
        name='spawn_piston_holder',
        output='screen',
        arguments=[
            '--model', 'piston_holder.urdf.xacro',
            '--name', 'piston_holder',
            '--x', '0.0',
            '--y', '0.0',
            '--z', '0.0',
        ],
    )

    spawn_base_component = Node(
        package='conveyor_belt',
        executable='spawn_static_model.py',
        name='spawn_base_component',
        output='screen',
        arguments=[
            '--model', 'base_component.urdf.xacro',
            '--name', 'base_component',
            '--x', '0.0',
            '--y', '0.0',
            '--z', '0.0',
        ],
    )

    spawn_second_conveyor = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_second_conveyor_belt',
        output='screen',
        arguments=[
            '-name', 'conveyor_belt_2',
            '-topic', '/robot_description',
            '-x', '-1.5',
            '-y', '4.5',
            '-z', '0.8',
            '-Y', '-1.5708',
        ],
    )

    spawn_base_component_delayed = TimerAction(
        period=4.0,
        actions=[spawn_base_component]
    )
    spawn_conveyor_delayed = TimerAction(period=5.0, actions=[spawn_conveyor])
    spawn_static_models_delayed = TimerAction(
        period=6.0,
        actions=[
            spawn_storage,
            spawn_scanner,
            spawn_ramp,
            spawn_piston_holder,
            spawn_second_conveyor,
        ]
    )

    return LaunchDescription([
        set_gz_resource_path,      # <-- must be first
        set_gz_plugin_path,
        use_sim_time_arg,
        gz_sim,
        robot_state_publisher,
        ros_gz_bridge,
        conveyor_relay,
        spawn_base_component_delayed,
        spawn_conveyor_delayed,
        spawn_static_models_delayed,
    ])
