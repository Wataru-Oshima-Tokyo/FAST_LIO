import os.path

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition

from launch_ros.actions import Node, SetUseSimTime

def launch_setup(context, *args, **kwargs):
    use_sim_time = LaunchConfiguration('use_sim_time')
    config_path = LaunchConfiguration('config_path').perform(context)
    rviz_use = LaunchConfiguration('rviz')
    rviz_cfg = LaunchConfiguration('rviz_cfg')
    map_name = LaunchConfiguration('map_name').perform(context)
    robot_type = LaunchConfiguration('robot_type').perform(context)
    map_location = LaunchConfiguration('map_location').perform(context)
    config_path += "/" + robot_type +"_mid360.yaml"
    map_dir = os.path.join(map_location, map_name)
        # Check if graph_dir does not exist and create it
    if not os.path.exists(map_dir):
        os.makedirs(map_dir, exist_ok=True)  # Create the directory if it doesn't exist
    print(config_path)
    static_map_to_odom_node =  Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='world_to_map',
            arguments=['0', '0', '0', '0', '0', '0', '1', 'map', 'odom']
    )

    fast_lio_node = Node(
        package='fast_lio',
        executable='fastlio_mapping',
        parameters=[config_path,
                    {'use_sim_time': use_sim_time}, {'mapping.map_name': map_name}, {'mapping.map_location': map_location}],
        output='screen'
    )
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_cfg],
        condition=IfCondition(rviz_use)
    )

    return [
        static_map_to_odom_node,
        fast_lio_node,
        rviz_node
    ]




def generate_launch_description():
    package_path = get_package_share_directory('fast_lio')
    default_rviz_config_path = os.path.join(
        package_path, 'rviz', 'fastlio.rviz')
    default_config_path = os.path.join(package_path, 'config')
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time', default_value='false',
        description='Use simulation (Gazebo) clock if true'
    )
    declare_config_path_cmd = DeclareLaunchArgument(
        'config_path', default_value=default_config_path,
        description='Yaml config file path'
    )
    declare_rviz_cmd = DeclareLaunchArgument(
        'rviz', default_value='true',
        description='Use RViz to monitor results'
    )
    declare_rviz_config_path_cmd = DeclareLaunchArgument(
        'rviz_cfg', default_value=default_rviz_config_path,
        description='RViz config file path'
    )
    declare_map_name_arg = DeclareLaunchArgument(
        'map_name', default_value='sh',
        description='Map name'
    )
    declare_map_location_arg = DeclareLaunchArgument(
        'map_location', default_value='map',
        description='Map location'
    )
    robot_type_arg = DeclareLaunchArgument(
        'robot_type', default_value='go2',
        description='robot_type'
    )

    return LaunchDescription([
        declare_use_sim_time_cmd,
        declare_config_path_cmd,
        declare_rviz_cmd,
        declare_rviz_config_path_cmd,
        declare_map_name_arg,
        declare_map_location_arg,
        robot_type_arg,
        OpaqueFunction(function=launch_setup)
    ])
 
