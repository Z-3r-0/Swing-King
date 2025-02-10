import math


def calculate_trajectory(x: float, speed: float, angle: int, initial_pos_y: float):
    """
    Calculates the vertical position (y) of the ball based on the horizontal distance (x).

    :param x: Horizontal distance traveled
    :param speed: Applied speed (m/s)
    :param angle: Launch angle (alpha) in degrees
    :param initial_pos_y: initial position of the ball
    :return: Vertical position (y) of the ball
    """

    angle_radians = math.radians(angle)
    cos_alpha = math.cos(angle_radians)
    tan_alpha = math.tan(angle_radians)

    cos_alpha = 0.1 if cos_alpha == 0 else cos_alpha  # Avoid division by zero if angle is 90°

    y = (-4.9 * (x ** 2)) / (speed ** 2 * cos_alpha ** 2) + tan_alpha * x + initial_pos_y
    return y

def calculate_traj_x(t: float, speed: float, angle: int, mass: float, initial_pos_x: float):
    """
    Calculates the horizontal position (x) of the ball based on the time (t).

    :param t: time elapsed since the impact
    :param speed: Applied speed (m/s)
    :param angle: Launch angle (alpha) in degrees
    :param mass: mass of the ball
    :param initial_pos_x: initial position of the ball
    :return: Horizontal position (x) of the ball
    """

    angle_radians = math.radians(angle)
    cos_alpha = math.cos(angle_radians)

    cos_alpha = 0.1 if cos_alpha == 0 else cos_alpha  # Avoid division by zero if angle is 90°

    x = (speed * 0.1 / mass) * cos_alpha * t + initial_pos_x

    return x