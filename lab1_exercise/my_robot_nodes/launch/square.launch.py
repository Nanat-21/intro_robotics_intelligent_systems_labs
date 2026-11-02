from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    side_length = LaunchConfiguration('side_length')

    control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('diffdrive_bot'),
                'launch',
                'control.launch.py'
            )
        )
    )

    rotate_server = Node(
        package='my_robot_nodes',
        executable='rotate_server',
        output='screen'
    )

    square_driver = Node(
        package='my_robot_nodes',
        executable='square_driver',
        parameters=[{'side_length': side_length}],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'side_length',
            default_value='0.5',
            description='Length of each square side in meters'
        ),
        control_launch,
        rotate_server,
        square_driver
    ])
