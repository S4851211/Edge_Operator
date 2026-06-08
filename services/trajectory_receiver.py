#!/usr/bin/env python3

import csv
import rclpy

from rclpy.node import Node
from geometry_msgs.msg import PoseArray


class TrajectoryReceiver(Node):

    def __init__(self):
        super().__init__("trajectory_receiver")

        self.subscription = self.create_subscription(
            PoseArray,
            "/learned_trajectory",
            self.callback,
            10,
        )

        self.get_logger().info(
            "Waiting for /learned_trajectory ..."
        )

    def callback(self, msg):

        count = len(msg.poses)

        self.get_logger().info(
            f"Received trajectory with {count} poses"
        )

        filename = "data/received_trajectory.csv"

        with open(filename, "w", newline="") as f:

            writer = csv.writer(f)

            writer.writerow(
                [
                    "x",
                    "y",
                    "z",
                    "qx",
                    "qy",
                    "qz",
                    "qw",
                ]
            )

            for pose in msg.poses:

                writer.writerow(
                    [
                        pose.position.x,
                        pose.position.y,
                        pose.position.z,
                        pose.orientation.x,
                        pose.orientation.y,
                        pose.orientation.z,
                        pose.orientation.w,
                    ]
                )

        self.get_logger().info(
            f"Saved {count} poses to {filename}"
        )


def main():

    rclpy.init()

    node = TrajectoryReceiver()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
