import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from lab_interfaces.action import DriveDistance
from my_robot_interfaces.action import Rotate


class SquareDriver(Node):
    def __init__(self):
        super().__init__('square_driver')

        self.declare_parameter('side_length', 0.5)
        self.side_length = float(
            self.get_parameter('side_length').value
        )

        self.drive_client = ActionClient(
            self, DriveDistance, '/drive_distance'
        )
        self.rotate_client = ActionClient(
            self, Rotate, '/rotate'
        )

    def run_square(self):
        self.get_logger().info('Waiting for action servers...')

        self.drive_client.wait_for_server()
        self.rotate_client.wait_for_server()

        for side in range(4):
            self.get_logger().info(
                f'Driving side {side + 1}/4'
            )

            drive_goal = DriveDistance.Goal()
            drive_goal.distance = self.side_length

            future = self.drive_client.send_goal_async(drive_goal)
            rclpy.spin_until_future_complete(self, future)

            drive_handle = future.result()
            if not drive_handle or not drive_handle.accepted:
                self.get_logger().error('Drive goal rejected.')
                return

            result_future = drive_handle.get_result_async()
            rclpy.spin_until_future_complete(self, result_future)

            if not result_future.result().result.reached:
                self.get_logger().error('Drive action failed.')
                return

            self.get_logger().info(
                f'Rotating after side {side + 1}/4'
            )

            rotate_goal = Rotate.Goal()
            rotate_goal.angle = 1.5708

            future = self.rotate_client.send_goal_async(rotate_goal)
            rclpy.spin_until_future_complete(self, future)

            rotate_handle = future.result()
            if not rotate_handle or not rotate_handle.accepted:
                self.get_logger().error('Rotate goal rejected.')
                return

            result_future = rotate_handle.get_result_async()
            rclpy.spin_until_future_complete(self, result_future)

            if result_future.result().status != 4:
                self.get_logger().error('Rotate action failed.')
                return

        self.get_logger().info('Square movement completed!')


def main(args=None):
    rclpy.init(args=args)
    node = SquareDriver()

    try:
        node.run_square()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
