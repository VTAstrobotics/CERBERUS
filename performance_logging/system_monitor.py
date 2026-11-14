#!/usr/bin/env python3
"""
This file includes ROS 2 node that logs Jetson hardware stats via psutil
while a VSLAM pipeline runs.

Metrics:
  CPU      : psutil.cpu_percent(), psutil.cpu_count()
  Memory   : psutil.virtual_memory()
  Network  : psutil.net_io_counters()
  Sensors  : psutil.sensors_temperatures(), psutil.sensors_fans()

Run:
  pip3 install psutil
  source /opt/ros/<distro>/setup.bash
  python3 system_monitor.py # default: 1 s interval
  python3 system_monitor.py --ros-args -p interval:=2.0
"""

import psutil
import rclpy
from rclpy.node import Node


class SystemMonitor(Node):
    def __init__(self):
        super().__init__('system_monitor')
        self.declare_parameter('interval', 1.0)
        interval = self.get_parameter('interval').value

        # Static info, logged once
        self.get_logger().info(
            f'CPU count: {psutil.cpu_count(logical=True)} logical, '
            f'{psutil.cpu_count(logical=False)} physical'
        )

        # Prime cpu_percent (first call always returns 0.0)
        psutil.cpu_percent(percpu=True)
        self.last_net = psutil.net_io_counters()
        self.interval = interval

        self.timer = self.create_timer(interval, self.sample)

    def sample(self):
        log = self.get_logger()

        # CPU 
        per_core = psutil.cpu_percent(percpu=True)
        total = sum(per_core) / len(per_core)
        cores = ' '.join(f'{p:4.1f}' for p in per_core)
        log.info(f'CPU  total {total:5.1f}% | per-core [{cores}]')

        # Memory
        vm = psutil.virtual_memory()
        log.info(
            f'MEM  {vm.percent:5.1f}% used | '
            f'{vm.used / 1e9:.2f} / {vm.total / 1e9:.2f} GB | '
            f'available {vm.available / 1e9:.2f} GB'
        )

        # Network (rate since last sample)
        net = psutil.net_io_counters()
        sent_rate = (net.bytes_sent - self.last_net.bytes_sent) / self.interval
        recv_rate = (net.bytes_recv - self.last_net.bytes_recv) / self.interval
        self.last_net = net
        log.info(
            f'NET  tx {sent_rate / 1e3:8.1f} KB/s | rx {recv_rate / 1e3:8.1f} KB/s | '
            f'drops in/out {net.dropin}/{net.dropout}'
        )

        # Sensors: temperatures 
        try:
            temps = psutil.sensors_temperatures()
        except AttributeError:
            temps = {}
        if temps:
            parts = []
            for chip, entries in temps.items():
                for e in entries:
                    label = e.label or chip
                    parts.append(f'{label}={e.current:.1f}C')
            log.info('TEMP ' + ' '.join(parts))
        else:
            log.warn('TEMP no temperature sensors reported')

        # Sensors: fans
        try:
            fans = psutil.sensors_fans()
        except AttributeError:
            fans = {}
        if fans:
            parts = [f'{e.label or chip}={e.current}RPM'
                     for chip, entries in fans.items() for e in entries]
            log.info('FAN  ' + ' '.join(parts))
        else:
            log.warn('FAN  no fan RPM reported')


def main():
    rclpy.init()
    node = SystemMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()