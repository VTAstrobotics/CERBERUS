import launch
from launch_ros.descriptions import ComposableNode 
from launch_ros.actions import ComposableNodeContainer
from launch import LaunchDescription

"""Launch file which brings up visual slam node configured for vlsam."""
def generate_launch_description():
    visual_slam_node = ComposableNode(
    name='visual_slam_node',
    package='isaac_ros_visual_slam',
    plugin="nvidia::isaac_ros::visual_slam::VisualSlamNode",
    parameters=[{
                'enable_rectified_pose': True,
                'use_sim_time': True,
                'denoise_input_images': False,
                'rectified_images': True,
                'enable_debug_mode': False,
                'debug_dump_path': '/tmp/cuvslam',
                'enable_slam_visualization': True,
                'enable_landmarks_view': True,
                'enable_observations_view': True,
                'map_frame': 'map',
                'odom_frame': 'odom',
                'base_frame': 'camera_link',
                'input_imu_frame': 'camera_gyro_optical_frame',
                'enable_imu_fusion': False,
                'enable_imu': True
                }],
    remappings=[('stereo_camera/left/image', '/stereo/left/image_raw'),
                ('stereo_camera/left/camera_info', '/stereo/left/camera_info'),
                ('stereo_camera/right/image', '/stereo/right/image_raw'),
                ('stereo_camera/right/camera_info', '/stereo/right/camera_info'),
                ('visual_slam/imu', '/imu')]
)
    visual_slam_container = ComposableNodeContainer(
        name='visual_slam_launch_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container_mt',
        composable_node_descriptions=[visual_slam_node],
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    return LaunchDescription([
        visual_slam_container
    ])

