import os
from launch import LaunchDescription

from launch_ros.actions import Node

VENV_SITE = os.path.expanduser('~/myenv/lib/python3.12/site-packages') + ':'


def generate_launch_description():
    spawn_gesture_recognition = Node(package="gesture_recognition",
        executable="gesture_node",
        name="gesture_node",
        parameters=[],
        additional_env={
        'PYTHONPATH': '/usr/lib/python3/dist-packages:' + VENV_SITE + os.environ.get('PYTHONPATH', '')
         }
    )

    return LaunchDescription([
        spawn_gesture_recognition,
    ])
