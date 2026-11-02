import asyncio
import math

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.executors import MultiThreadedExecutor
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from my_robot_interfaces.action import Rotate


def yaw_from_quaternion(q):
    return math.atan2(
        2.0 * (q.w * q.z + q.x * q.y),
        1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    )


def angle_difference(current, previous):
    return math.atan2(
        math.sin(current - previous),
        math.cos(current - previous)
    )


class RotateServer(Node):

    def __init__(self):
        super().__init__('rotate_server')

        self.declare_parameter('turn_speed', 0.5)

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.last_yaw = None
        self.total_yaw = 0.0
        self.active = False

        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10
        )

        self.action_server = ActionServer(
            self,
            Rotate,
            '/rotate',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )

        self.get_logger().info('Rotate action server ready.')

    def odom_callback(self, msg):
        yaw = yaw_from_quaternion(msg.pose.pose.orientation)

        if self.last_yaw is not None and self.active:
            self.total_yaw += angle_difference(yaw, self.last_yaw)

        self.last_yaw = yaw

    def goal_callback(self, goal):
        if goal.angle == 0.0 or self.active:
            return GoalResponse.REJECT
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        self.active = True
        self.total_yaw = 0.0

        direction = 1.0 if goal_handle.request.angle > 0 else -1.0
        target = abs(float(goal_handle.request.angle))

        command = Twist()
        command.angular.z = (
            direction * float(self.get_parameter('turn_speed').value)
        )

        self.cmd_pub.publish(command)

        feedback = Rotate.Feedback()

        try:
            while direction * self.total_yaw < target:
                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                    return Rotate.Result()

                feedback.turned = float(self.total_yaw)
                goal_handle.publish_feedback(feedback)

                await asyncio.sleep(0.05)

            goal_handle.succeed()

            result = Rotate.Result()
            result.turned = float(self.total_yaw)
            return result

        finally:
            self.cmd_pub.publish(Twist())
            self.active = False


def main(args=None):
    rclpy.init(args=args)
    node = RotateServer()

    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.cmd_pub.publish(Twist())
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
