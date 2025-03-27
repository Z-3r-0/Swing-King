import pygame
import math

drag_data = {
    "dragging": False,
    "start_pos": (0, 0),
    "release_velocity": (0.0, 0.0)
}


def handle_drag_and_release(ball_position, ball_radius=10):
    """
    Handles mouse drag and release to calculate velocity.

    Args:
        ball_position (tuple): Current (x, y) position of the ball.
        ball_radius (int): Radius of the ball (default: 10).

    Returns:
        tuple: (velocity_x, velocity_y) after release, or None if no release.
    """
    global drag_data

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return None  # Quit event

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse click
        mouse_x, mouse_y = pygame.mouse.get_pos()
        distance = math.hypot(mouse_x - ball_position[0], mouse_y - ball_position[1])
        print("Distance :", distance)
        if distance <= ball_radius:  # Start drag only if near the ball
            drag_data["dragging"] = True
            drag_data["start_pos"] = (mouse_x, mouse_y)

    if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and drag_data["dragging"]:
        end_x, end_y = pygame.mouse.get_pos()
        drag_data["dragging"] = False  # Stop dragging

        # Compute velocity
        dx, dy = end_x - drag_data["start_pos"][0], end_y - drag_data["start_pos"][1]
        force = min(math.hypot(dx, dy), 20)  # Limit max force
        angle = math.atan2(dy, dx)

        # Decompose into velocity components
        velocity_x = math.cos(angle) * force
        velocity_y = math.sin(angle) * force

        drag_data["release_velocity"] = (velocity_x, velocity_y)
        print("Release velocity:", drag_data["release_velocity"])

        return velocity_x, velocity_y  # Return velocity when released

    return None  # No release event yet
