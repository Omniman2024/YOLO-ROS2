#!/usr/bin/env python3
"""
conveyor_relay.py

Subscribes to /conveyor_power (std_msgs/Bool) to set belt on/off.
Continuously publishes velocity at 10 Hz to keep JointController active.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Float64

MAX_VELOCITY = 0.3  # m/s


class ConveyorRelay(Node):

    def __init__(self):
        super().__init__('conveyor_relay')

        self.belt_on = False

        self.publisher_ = self.create_publisher(
            Float64,
            '/model/conveyor_belt/joint/belt_joint/cmd_vel',
            10
        )
        self.publisher_secondary_ = self.create_publisher(
            Float64,
            '/model/conveyor_belt_2/joint/belt_joint/cmd_vel',
            10
        )
        self.publisher_tertiary_ = self.create_publisher(
            Float64,
            '/model/conveyor_belt_3/joint/belt_joint/cmd_vel',
            10
        )

        self.subscription = self.create_subscription(
            Bool,
            '/conveyor_power',
            self.on_power,
            10
        )

        # Publish at 10 Hz continuously
        self.timer = self.create_timer(0.1, self.publish_velocity)

        self.get_logger().info('ConveyorRelay ready.')

    def on_power(self, msg: Bool):
        self.belt_on = msg.data
        self.get_logger().info(f'Belt power: {"ON" if self.belt_on else "OFF"}')

    def publish_velocity(self):
        cmd = Float64()
        cmd.data = MAX_VELOCITY if self.belt_on else 0.0
        self.publisher_.publish(cmd)
        self.publisher_secondary_.publish(cmd)
        self.publisher_tertiary_.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = ConveyorRelay()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
