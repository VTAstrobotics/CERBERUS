import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'gesture_recognition'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'resource'), glob('resource/yolo11n-pose.pt')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*')),
        (os.path.join('share', package_name, 'config'), glob("config/*")),
    ],
    install_requires=['setuptools','ultralytics'],
    zip_safe=True,
    maintainer='astro-dev',
    maintainer_email='cfernandez06@vt.edu',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'gesture_node = gesture_recognition.gesture_recognition:main'
        ],
    },
)
