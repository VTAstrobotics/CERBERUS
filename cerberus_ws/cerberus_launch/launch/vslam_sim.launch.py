import launch
from launch_ros.actions import Node 

"""Launch file which brings up visual slam node configured for vlsam."""

visual_slam_node = Node(
    name='visual_slam_node',
    package='isaac_ros_visual_slam',
    plugin='isaac_ros::visual_slam::VisualSlamNode',
    executable="isaac_ros_visual_slam",
    parameters=[{
                'enable_rectified_pose': True,
                'denoise_input_images': False,
                'rectified_images': True,
                'enable_debug_mode': False,
                'debug_dump_path': '/tmp/elbrus',
                'enable_slam_visualization': True,
                'enable_landmarks_view': True,
                'enable_observations_view': True,
                'map_frame': 'map',
                'odom_frame': 'odom',
                'base_frame': 'camera_link',
                'input_imu_frame': 'camera_gyro_optical_frame',
                'enable_imu': True
                }],
    remappings=[('stereo_camera/left/image', '/stereo/left/image_raw'),
                ('stereo_camera/left/camera_info', 'stereo/left/camera_info'),
                ('stereo_camera/right/image', '/stereo/right/image_raw'),
                ('stereo_camera/right/camera_info', '/stereo/right/camera_info'),
                ('visual_slam/imu', '/imu')]
)
