import math
from src import physics
import pygame


def drag_and_release(start_pos, end_pos):
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    distance = min(math.hypot(dx, dy), 500)  # Limit the force
    angle = math.degrees(math.atan2(-dy, dx))  # Natural direction from the center
    force = distance * 5.0  # Greatly increased force to propel the ball further
    return force, angle


def draw_predicted_trajectory(
    surface: pygame.Surface,
    start_pos: pygame.Vector2,
    initial_velocity: pygame.Vector2,
    gravity_accel: float, # Renamed for clarity
    base_damping_factor: float, # Renamed for clarity
    dt: float, # Time step for each prediction step
    steps: int,
    camera_offset: pygame.Vector2,
    color: tuple,
    radius: int,
    spacing: int
):
    if initial_velocity.length_squared() == 0:
        return

    position = start_pos.copy()
    velocity = initial_velocity.copy()
    steps_since_last_dot = 0

    # Calculate effective damping for this dt, same as in main physics
    effective_damping_per_step = base_damping_factor ** dt

    for i in range(steps):
        # Update velocity (gravity and damping)
        velocity.y += gravity_accel * dt
        velocity *= effective_damping_per_step # Apply consistent damping

        # Update position
        position += velocity * dt

        # Draw dot periodically
        steps_since_last_dot += 1
        if steps_since_last_dot >= spacing:
            screen_pos = position - camera_offset
            pygame.draw.circle(surface, color, screen_pos, radius)
            steps_since_last_dot = 0

        if velocity.length_squared() < (physics.BALL_STOP_SPEED_THRESHOLD ** 2): # Optional: stop if slow
            break