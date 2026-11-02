import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from lab_interfaces.msg import ObstacleInfo
from my_robot_interfaces.msg import RobotStatus
from my_robot_interfaces.srv import SetTurnSpeed
from std_srvs.srv import SetBool


class TurnAway(Node):

    def __init__(self):
        super().__init__('turn_away')

        self.declare_parameter('forward_speed', 0.2)
        self.declare_parameter('turn_speed', 0.5)
        self.declare_parameter('max_turn_speed', 1.5)

        self.enabled = False
        self.last_distance = 0.0

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.status_pub = self.create_publisher(
            RobotStatus, '/robot_status', 10
        )

        self.obstacle_sub = self.create_subscription(
            ObstacleInfo, '/obstacle', self.obstacle_callback, 10
        )

        self.enable_service = self.create_service(
            SetBool, '/turn_away_enable', self.enable_callback
        )

        self.speed_service = self.create_service(
            SetTurnSpeed, '/set_turn_speed', self.speed_callback
        )

        self.get_logger().info('Turn away node started (disabled).')

    def enable_callback(self, request, response):
        self.enabled = request.data

        if not self.enabled:
            self.cmd_pub.publish(Twist())

        response.success = True
        response.message = 'Turn away enabled' if self.enabled else 'Turn away disabled'
        return response

    def speed_callback(self, request, response):
        speed = request.turn_speed
        maximum = self.get_parameter('max_turn_speed').value

        if speed <= 0.0 or speed > maximum:
            response.success = False
            response.message = f'Speed must be greater than 0 and at most {maximum}.'
        else:
            self.set_parameters([
                rclpy.parameter.Parameter(
                    'turn_speed',
                    rclpy.Parameter.Type.DOUBLE,
                    float(speed)
                )
            ])
            response.success = True
            response.message = f'Turn speed set to {speed}.'

        return response

    def obstacle_callback(self, msg):
        self.last_distance = float(msg.distance)

        command = Twist()
        status = RobotStatus()
        status.obstacle_distance = self.last_distance

        if not self.enabled:
            status.state = 'stopped'
        elif not msg.too_close:
            command.linear.x = float(
                self.get_parameter('forward_speed').value
            )
            status.state = 'forward'
        else:
            speed = float(self.get_parameter('turn_speed').value)
            command.angular.z = -speed if msg.angle > 0.0 else speed
            status.state = 'turning'

        if self.enabled:
            self.cmd_pub.publish(command)

        self.status_pub.publish(status)


def main(args=None):
    rclpy.init(args=args)
    node = TurnAway()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cmd_pub.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
