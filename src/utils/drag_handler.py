import math
import pygame

# Max distance for full power drag
MAX_DRAG_DISTANCE = 300.0
# Factor to convert drag distance to force magnitude
FORCE_SCALING_FACTOR = 5.0 # Adjust this to change sensitivity

def calculate_shot_parameters(ball_screen_pos: pygame.Vector2, mouse_pos: pygame.Vector2, max_force: float, min_force_threshold: float):
    """
    Calculates the force magnitude and angle for the shot based on mouse drag.

    Args:
        ball_screen_pos: The screen position (Vector2) of the ball's center.
        mouse_pos: The current screen position (Vector2) of the mouse.
        max_force: The maximum possible force magnitude.
        min_force_threshold: The minimum force required to register a shot.

    Returns:
        A tuple (force, angle_degrees):
        - force (float): The magnitude of the force to apply (0 if below threshold).
        - angle_degrees (float): The angle of the shot direction in degrees
                                 (0-360, counter-clockwise from positive x-axis).
                                 Returns 0 if force is 0.
    """
    drag_vector = mouse_pos - ball_screen_pos # Vector from ball towards mouse

    if drag_vector.length_squared() == 0:
        return 0, 0

    # Calculate distance and clamp it
    distance = drag_vector.length()
    clamped_distance = min(distance, MAX_DRAG_DISTANCE)

    # Calculate force based on clamped distance
    force = (clamped_distance / MAX_DRAG_DISTANCE) * max_force

    # Check against minimum threshold
    if force < min_force_threshold:
        return 0, 0

    # Calculate the angle of the vector pointing *away* from the drag
    # This is the direction the ball should travel
    shot_vector = -drag_vector
    angle_radians = math.atan2(shot_vector.y, shot_vector.x) # Note: Pygame y is inverted, but atan2 handles it

    # Convert to degrees (0-360)
    angle_degrees = math.degrees(angle_radians)
    angle_degrees = (angle_degrees + 360) % 360 # Normalize to 0-360

    return force, angle_degrees

def draw_drag_line(surface: pygame.Surface, start_pos: pygame.Vector2, end_pos: pygame.Vector2, color: tuple, width: int):
    """Draws the visual drag indicator line."""
    pygame.draw.line(surface, color, start_pos, end_pos, width)
