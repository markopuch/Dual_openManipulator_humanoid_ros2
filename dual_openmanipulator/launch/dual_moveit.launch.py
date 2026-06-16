#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro
import yaml


def load_yaml(package_name, relative_path):
    package_path = get_package_share_directory(package_name)
    absolute_path = os.path.join(package_path, relative_path)
    with open(absolute_path, 'r') as file:
        return yaml.safe_load(file)


def load_text(package_name, relative_path):
    package_path = get_package_share_directory(package_name)
    absolute_path = os.path.join(package_path, relative_path)
    with open(absolute_path, 'r') as file:
        return file.read()


def generate_launch_description():
    pkg_share = get_package_share_directory('dual_openmanipulator')
    use_sim_time = LaunchConfiguration('use_sim_time')
    launch_rviz = LaunchConfiguration('launch_rviz')

    robot_description_config = xacro.process_file(
        os.path.join(pkg_share, 'urdf', 'dual_open_manipulator.urdf.xacro'),
        mappings={'use_sim': 'true'},
    )
    robot_description = {'robot_description': robot_description_config.toxml()}

    robot_description_semantic = {
        'robot_description_semantic': load_text(
            'dual_openmanipulator',
            'config/dual_open_manipulator.srdf',
        )
    }

    kinematics_yaml = load_yaml('dual_openmanipulator', 'config/kinematics.yaml')
    joint_limits_yaml = load_yaml('dual_openmanipulator', 'config/joint_limits.yaml')
    ompl_planning_yaml = load_yaml('dual_openmanipulator', 'config/ompl_planning.yaml')
    moveit_controllers_yaml = load_yaml(
        'dual_openmanipulator',
        'config/moveit_controllers.yaml',
    )

    ompl_planning_pipeline_config = {
        'move_group': {
            'planning_plugin': 'ompl_interface/OMPLPlanner',
            'request_adapters': (
                'default_planner_request_adapters/AddTimeOptimalParameterization '
                'default_planner_request_adapters/FixWorkspaceBounds '
                'default_planner_request_adapters/FixStartStateBounds '
                'default_planner_request_adapters/FixStartStateCollision '
                'default_planner_request_adapters/FixStartStatePathConstraints'
            ),
            'start_state_max_bounds_error': 0.1,
        }
    }
    ompl_planning_pipeline_config['move_group'].update(ompl_planning_yaml)

    trajectory_execution = {
        'moveit_manage_controllers': False,
        'trajectory_execution.allowed_execution_duration_scaling': 1.2,
        'trajectory_execution.allowed_goal_duration_margin': 0.5,
        'trajectory_execution.allowed_start_tolerance': 0.01,
    }

    moveit_controllers = {
        'moveit_simple_controller_manager': moveit_controllers_yaml,
        'moveit_controller_manager':
            'moveit_simple_controller_manager/MoveItSimpleControllerManager',
    }

    planning_scene_monitor_parameters = {
        'publish_planning_scene': True,
        'publish_geometry_updates': True,
        'publish_state_updates': True,
        'publish_transforms_updates': True,
        'publish_robot_description': True,
        'publish_robot_description_semantic': True,
    }

    common_parameters = [
        robot_description,
        robot_description_semantic,
        kinematics_yaml,
        joint_limits_yaml,
        ompl_planning_pipeline_config,
        trajectory_execution,
        moveit_controllers,
        planning_scene_monitor_parameters,
        {'use_sim_time': use_sim_time},
    ]

    move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=common_parameters,
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(pkg_share, 'config', 'dual_moveit.rviz')],
        parameters=common_parameters,
        condition=IfCondition(launch_rviz),
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use Gazebo simulation clock.',
        ),
        DeclareLaunchArgument(
            'launch_rviz',
            default_value='true',
            description='Open RViz with the MoveIt MotionPlanning panel.',
        ),
        move_group_node,
        rviz_node,
    ])
