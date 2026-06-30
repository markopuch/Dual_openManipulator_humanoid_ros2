#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.actions import RegisterEventHandler
from launch.actions import SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.conditions import UnlessCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch.substitutions import FindExecutable
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = get_package_share_directory('bimanual_setup_description')
    gazebo_ros_share = get_package_share_directory('gazebo_ros')
    open_manipulator_share = get_package_share_directory('open_manipulator_x_description')

    use_sim_time = LaunchConfiguration('use_sim_time')
    gui = LaunchConfiguration('gui')
    world = LaunchConfiguration('world')
    use_combined_controller = LaunchConfiguration('use_combined_controller')

    robot_description = ParameterValue(
        Command([
            PathJoinSubstitution([FindExecutable(name='xacro')]),
            ' ',
            PathJoinSubstitution([
                FindPackageShare('bimanual_setup_description'),
                'urdf',
                'bimanual_setup.urdf.xacro',
            ]),
            ' ',
            'initial_positions_file:=',
            PathJoinSubstitution([
                FindPackageShare('bimanual_setup_description'),
                'config',
                'initial_joint_positions.yaml',
            ]),
        ]),
        value_type=str,
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_description},
            {'use_sim_time': use_sim_time},
        ],
    )

    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_share, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={
            'world': world,
            'verbose': 'false',
        }.items(),
    )

    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_share, 'launch', 'gzclient.launch.py')
        ),
        condition=IfCondition(gui),
    )

    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        output='screen',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'bimanual_setup',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.0',
        ],
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen',
    )

    left_arm_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['left_arm_controller', '--controller-manager', '/controller_manager'],
        output='screen',
        condition=UnlessCondition(use_combined_controller),
    )

    right_arm_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['right_arm_controller', '--controller-manager', '/controller_manager'],
        output='screen',
        condition=UnlessCondition(use_combined_controller),
    )

    both_arms_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['both_arms_controller', '--controller-manager', '/controller_manager'],
        output='screen',
        condition=IfCondition(use_combined_controller),
    )

    left_gripper_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['left_gripper_controller', '--controller-manager', '/controller_manager'],
        output='screen',
    )

    right_gripper_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['right_gripper_controller', '--controller-manager', '/controller_manager'],
        output='screen',
    )

    start_joint_state_broadcaster = RegisterEventHandler(
        OnProcessExit(
            target_action=spawn_robot,
            on_exit=[joint_state_broadcaster_spawner],
        )
    )

    start_motion_controllers = RegisterEventHandler(
        OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[
                left_arm_controller_spawner,
                right_arm_controller_spawner,
                both_arms_controller_spawner,
                left_gripper_controller_spawner,
                right_gripper_controller_spawner,
            ],
        )
    )

    model_paths = os.pathsep.join([
        os.path.join(open_manipulator_share, '..'),
        os.path.join(pkg_share, '..'),
    ])

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument(
            'world',
            default_value=os.path.join(pkg_share, 'worlds', 'lab_empty.world'),
        ),
        DeclareLaunchArgument(
            'use_combined_controller',
            default_value='false',
            description='false: left/right controllers active; true: one controller for both arms.',
        ),
        SetEnvironmentVariable('GAZEBO_MODEL_DATABASE_URI', ''),
        SetEnvironmentVariable('GAZEBO_MODEL_PATH', model_paths),
        gzserver,
        gzclient,
        robot_state_publisher,
        spawn_robot,
        start_joint_state_broadcaster,
        start_motion_controllers,
    ])
