import math

import pygame


def drag_and_release(start_pos, end_pos):
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    distance = min(math.hypot(dx, dy), 500)  # Limit the force
    angle = math.degrees(math.atan2(-dy, dx))  # Natural direction from the center
    force = distance * 5.0  # Greatly increased force to propel the ball further
    return force, angle


def draw_predicted_trajectory(start_pos, force, angle, gravity, fps, screen):
    # Calculate the initial velocity vector from the center of the ball
    initial_velocity = pygame.Vector2(
        -force * math.cos(math.radians(angle)),
        force * math.sin(math.radians(angle))
    )

    # Incorporation of friction in the prediction:
    # k is the continuous friction coefficient, such that exp(-k) ~ 0.98 over one frame.
    k = -math.log(0.98) * fps

    # Draw only the beginning of the trajectory (for example during 0.75 seconds)
    t = 0.0
    dt_sim = 0.1  # Fewer points for a cleaner trajectory
    while t < 0.75:
        # Predicted position incorporating friction and gravity:
        pred_x = start_pos.x + (initial_velocity.x / k) * (1 - math.exp(-k * t))
        pred_y = start_pos.y + ((initial_velocity.y - gravity / k) / k) * (1 - math.exp(-k * t)) + (gravity * t / k)
        pygame.draw.circle(screen, pygame.Color("white"), (int(pred_x), int(pred_y)), 3)
        t += dt_sim