from launch import LaunchDescription

from launch_ros.actions import Node

def generate_launch_description():
    spawn_gesture_recognition = Node(package="gesture_recognition",            
        executable="gesture_node",
        name="gesture_node",
        parameters=[]
         additional_env={
        'PYTHONPATH': '/usr/lib/python3/dist-packages:' + os.environ.get('PYTHONPATH', '')
         }
    )


    return LaunchDescription([
        spawn_gesture_recognition,
    ])