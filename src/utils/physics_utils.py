import math


def calculate_trajectory(x: float, force: float, angle: int):
    """
    Calculates the vertical position (y) of the ball based on the horizontal distance (x).

    :param x: Horizontal distance traveled
    :param force: Applied force
    :param angle: Launch angle (alpha) in degrees
    :return: Vertical position (y) of the ball
    """

    angle_radians = math.radians(angle)
    cos_alpha = math.cos(angle_radians)
    tan_alpha = math.tan(angle_radians)

    cos_alpha = 0.1 if cos_alpha == 0 else cos_alpha  # Avoid division by zero if angle is 90°

    y = (-4.9 * (x ** 2)) / (force ** 2 * cos_alpha ** 2) + tan_alpha * x
    return y
