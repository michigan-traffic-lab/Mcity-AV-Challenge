import math
import numpy as np


max_accel = 2.87  # m/s^2
max_decel = 7.06  # m/s^2
max_jerk = 10  # m/s^3
max_slip_angle = math.radians(15)  # radians
max_yaw_rate = math.radians(50)  # radians/s
resolution = 0.1


def rotate_point2_around_point1(point1, point2, angle):
    """
    Rotate point2 around point1 clockwise by the given angle.

    Args:
        point1 (list): The first point.
        point2 (list): The second point.
        angle (float): The angle in radians.

    Returns:
        list: The rotated point.
    """
    x1, y1 = point1
    x2, y2 = point2

    x = x1 + math.cos(angle) * (x2 - x1) + math.sin(angle) * (y2 - y1)
    y = y1 - math.sin(angle) * (x2 - x1) + math.cos(angle) * (y2 - y1)
    return [x, y]


def checking(step_info, planning_result):
    """
    Check the vehicle kinematics based on the current step information and the planning result.

    Args:
        step_info (dict): The current step information.
        planning_result (dict): The planning result.

    Returns:
        None
    """
    av_info = step_info["av_info"]
    current_x = av_info["x"]
    current_y = av_info["y"]
    current_orientation = av_info["orientation"]
    current_speed_long = av_info["speed_long"]
    current_speed_lat = av_info["speed_lat"]
    current_accel_long = av_info["accel_long"]
    current_accel_lat = av_info["accel_lat"]

    next_x = planning_result["next_x"]
    next_y = planning_result["next_y"]
    next_orientation = planning_result["next_orientation"]

    rotated_position = rotate_point2_around_point1(
        [current_x, current_y], [next_x, next_y], current_orientation
    )
    next_speed_long = (rotated_position[0] - current_x) / resolution
    next_speed_lat = (rotated_position[1] - current_y) / resolution

    # step 1. check acceleration
    next_accel_long = (next_speed_long - current_speed_long) / resolution
    next_accel_lat = (next_speed_lat - current_speed_lat) / resolution
    if next_accel_long >= 0:
        overall_accel = np.sqrt(next_accel_long**2 + next_accel_lat**2)
        if overall_accel > max_accel:
            print(
                f"--------Warning: The overall acceleration ({overall_accel}) is higher than the maximum acceleration ({max_accel})."
            )
    else:
        overall_decel = np.sqrt(next_accel_long**2 + next_accel_lat**2)
        if overall_decel > max_decel:
            print(
                f"--------Warning: The overall deceleration ({overall_decel}) is higher than the maximum deceleration ({max_decel})."
            )

    # step 2. check jerk
    next_jerk_long = (next_accel_long - current_accel_long) / resolution
    next_jerk_lat = (next_accel_lat - current_accel_lat) / resolution
    overall_jerk = np.sqrt(next_jerk_long**2 + next_jerk_lat**2)
    if overall_jerk > max_jerk:
        print(
            f"--------Warning: The overall jerk ({overall_jerk}) is higher than the maximum jerk ({max_jerk})."
        )

    # step 3. check slip angle
    if next_speed_long == 0 and next_speed_lat == 0:
        slip_angle = 0
    elif next_speed_long == 0 and next_speed_lat > 0:
        slip_angle = math.pi / 2
    elif next_speed_long == 0 and next_speed_lat < 0:
        slip_angle = -math.pi / 2
    else:
        slip_angle = math.atan(next_speed_lat / next_speed_long)
    if abs(slip_angle) > max_slip_angle:
        print(
            f"--------Warning: The absolute value of slip angle ({slip_angle}) is higher than the maximum slip angle ({max_slip_angle})."
        )

    # step 4. check yaw rate
    delta_orientation = next_orientation - current_orientation
    delta_orientation = math.atan2(
        math.sin(delta_orientation), math.cos(delta_orientation)
    )
    yaw_rate = delta_orientation / resolution
    if abs(yaw_rate) > max_yaw_rate:
        print(
            f"--------Warning: The absolute value of yaw rate ({yaw_rate}) is higher than the maximum yaw rate ({max_yaw_rate})."
        )
