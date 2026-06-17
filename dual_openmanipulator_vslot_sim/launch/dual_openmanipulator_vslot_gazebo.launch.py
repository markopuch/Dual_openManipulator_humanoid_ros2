#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.actions import RegisterEventHandler
from launch.actions import SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch.substitutions import FindExecutable
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare
import yaml


def load_position_defaults(package_share):
    config_path = os.path.join(package_share, 'config', 'dual_arm_vslot_positions.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)['vslot']


def generate_launch_description():
    pkg_share = get_package_share_directory('dual_openmanipulator_vslot_sim')
    gazebo_ros_share = get_package_share_directory('gazebo_ros')
    description_share = get_package_share_directory('open_manipulator_x_description')
    dual_share = get_package_share_directory('dual_openmanipulator')
    defaults = load_position_defaults(pkg_share)

    use_sim_time = LaunchConfiguration('use_sim_time')
    gui = LaunchConfiguration('gui')
    world = LaunchConfiguration('world')
    base_x = LaunchConfiguration('base_x')
    base_y = LaunchConfiguration('base_y')
    base_z = LaunchConfiguration('base_z')
    column_height = LaunchConfiguration('column_height')
    beam_length = LaunchConfiguration('beam_length')
    left_mount_x = LaunchConfiguration('left_mount_x')
    right_mount_x = LaunchConfiguration('right_mount_x')
    arm_base_z_offset = LaunchConfiguration('arm_base_z_offset')
    left_arm_yaw = LaunchConfiguration('left_arm_yaw')
    right_arm_yaw = LaunchConfiguration('right_arm_yaw')

    robot_description = ParameterValue(
        Command([
            PathJoinSubstitution([FindExecutable(name='xacro')]),
            ' ',
            PathJoinSubstitution([
                FindPackageShare('dual_openmanipulator_vslot_sim'),
                'urdf',
                'dual_openmanipulator_vslot.urdf.xacro',
            ]),
            ' ',
            'use_sim:=true',
            ' ',
            'base_x:=', base_x,
            ' ',
            'base_y:=', base_y,
            ' ',
            'base_z:=', base_z,
            ' ',
            'column_height:=', column_height,
            ' ',
            'beam_length:=', beam_length,
            ' ',
            'left_mount_x:=', left_mount_x,
            ' ',
            'right_mount_x:=', right_mount_x,
            ' ',
            'arm_base_z_offset:=', arm_base_z_offset,
            ' ',
            'left_arm_yaw:=', left_arm_yaw,
            ' ',
            'right_arm_yaw:=', right_arm_yaw,
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
            '-entity', 'dual_openmanipulator_vslot',
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

    arm_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['vslot_dual_arm_controller', '--controller-manager', '/controller_manager'],
        output='screen',
    )

    left_gripper_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['left_vslot_gripper_controller', '--controller-manager', '/controller_manager'],
        output='screen',
    )

    right_gripper_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['right_vslot_gripper_controller', '--controller-manager', '/controller_manager'],
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
                arm_controller_spawner,
                left_gripper_controller_spawner,
                right_gripper_controller_spawner,
            ],
        )
    )

    model_paths = os.pathsep.join([
        os.path.join(description_share, '..'),
        os.path.join(dual_share, '..'),
        os.path.join(pkg_share, '..'),
    ])

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument(
            'world',
            default_value=os.path.join(pkg_share, 'worlds', 'dual_arm_vslot_demo.world'),
        ),
        DeclareLaunchArgument('base_x', default_value=str(defaults['base_x'])),
        DeclareLaunchArgument('base_y', default_value=str(defaults['base_y'])),
        DeclareLaunchArgument('base_z', default_value=str(defaults['base_z'])),
        DeclareLaunchArgument('column_height', default_value=str(defaults['column_height'])),
        DeclareLaunchArgument('beam_length', default_value=str(defaults['beam_length'])),
        DeclareLaunchArgument('left_mount_x', default_value=str(defaults['left_mount_x'])),
        DeclareLaunchArgument('right_mount_x', default_value=str(defaults['right_mount_x'])),
        DeclareLaunchArgument(
            'arm_base_z_offset',
            default_value=str(defaults['arm_base_z_offset']),
        ),
        DeclareLaunchArgument('left_arm_yaw', default_value=str(defaults['left_arm_yaw'])),
        DeclareLaunchArgument('right_arm_yaw', default_value=str(defaults['right_arm_yaw'])),
        SetEnvironmentVariable('GAZEBO_MODEL_DATABASE_URI', ''),
        SetEnvironmentVariable('GAZEBO_MODEL_PATH', model_paths),
        gzserver,
        gzclient,
        robot_state_publisher,
        spawn_robot,
        start_joint_state_broadcaster,
        start_motion_controllers,
    ])
