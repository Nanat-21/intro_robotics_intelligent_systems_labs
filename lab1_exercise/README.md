# Lab 1 – Robotics Exercise

## Overview
This exercise extends the differential-drive robot using ROS 2 Humble and Gazebo Harmonic. It includes additional sensors, custom ROS interfaces, and Python nodes for robot control.

## Packages

The exercise contains four ROS 2 packages:

- `diffdrive_bot` – robot description, Gazebo configuration, sensor setup, and launch files.
- `lab_interfaces` – existing obstacle and drive-distance interfaces.
- `my_robot_interfaces` – custom `RobotStatus` message, `SetTurnSpeed` service, and `Rotate` action.
- `my_robot_nodes` – obstacle-avoidance, rotation-server, and square-driver nodes.

## Requirements

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Harmonic
- `colcon`

## Build

From the ROS 2 workspace:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

## Run

To launch the robot simulation and control environment:

```bash
ros2 launch diffdrive_bot control.launch.py
```

To run the obstacle-avoidance node in another terminal:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run my_robot_nodes turn_away
```

The obstacle-avoidance node starts disabled. It can be enabled using the `/turn_away_enable` service.

To launch the square-driving integration:

```bash
ros2 launch my_robot_nodes square.launch.py
```

## Implemented Features

- Added a depth camera and IMU to the robot.
- Configured Gazebo sensor plugins and ROS-Gazebo bridges.
- Created custom ROS 2 message, service, and action interfaces.
- Implemented an obstacle-avoidance node with configurable speeds.
- Implemented a rotation action server with odometry feedback.
- Implemented a square-driving client that sends drive and rotation goals.

## Testing and Results

- All four packages built successfully using `colcon build`.
- Depth camera image and point-cloud topics were available in the simulation.
- IMU messages were received.
- The turn-away enable service and turn-speed service were tested.
- The robot-status topic and forward velocity command were verified.
- The square-driving launch started its nodes, but the first drive-distance goal was rejected. Therefore, successful completion of the square movement has not been verified.

## Screenshots

### RViz – Depth Camera and Point Cloud

![RViz depth camera and point cloud](screenshots/depth_camera_pointcloud.png)

