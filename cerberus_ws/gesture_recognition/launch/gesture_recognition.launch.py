from launch import LaunchDescription

from launch_ros.actions import Node

def generate_launch_description():
    spawn_gesture_recognition = Node(package="gesture_recognition",            
        executable="gesture_node",
        name="gesture_node",
        parameters=[]
    )


    return LaunchDescription([
        spawn_gesture_recognition,
    ])