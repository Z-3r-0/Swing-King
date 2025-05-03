import pygame
import math

# Import necessary classes from entities
from src.entities.terrain import Terrain
from src.entities.obstacle import Obstacle
# Import utility functions
from src.utils.physics_utils import get_polygon_collision_normal_depth

# --- Constants ---
GRAVITY = 980.0  # Gravitational acceleration in pixels/s²
DEFAULT_DAMPING = 0.99 # Velocity multiplier per frame to simulate air/rolling resistance
STOP_SPEED_THRESHOLD = 8.0 # Speed (pixels/s) below which the ball stops
MIN_BOUNCE_VELOCITY = 15.0 # Minimum velocity component normal to surface after bounce
COLLISION_PUSH_FACTOR = 1.01 # Slightly > 1 to push ball out of collision
MAX_COLLISION_ITERATIONS = 3 # Max times to re-check collisions within one sub-step

# --- Core Physics Update Function ---

def update_ball_physics(ball, terrain_polys, obstacles, dt):
    """
    Updates the ball's position, velocity, and handles collisions for one fixed sub-step (dt).

    Args:
        ball: The Ball object.
        terrain_polys: List of Terrain objects.
        obstacles: List of Obstacle objects.
        dt: Fixed time delta for the sub-step (in seconds).

    Returns:
        bool: True if the ball is still considered moving after this sub-step, False otherwise.
    """
    if not ball.is_moving:
        return False

    # 1. Apply Forces (Gravity and Damping)
    ball.velocity.y += GRAVITY * dt
    # Apply damping based on the fixed dt. If dt is very small, damping effect per step is also small.
    ball.velocity *= (DEFAULT_DAMPING ** (dt * 60)) # Frame-rate independent damping approximation

    # 2. Update Position based on current velocity
    ball.position += ball.velocity * dt
    ball.rect.center = ball.position # Keep rect updated

    # 3. Iterative Collision Detection and Resolution Loop
    collidable_objects = terrain_polys + [obs for obs in obstacles if obs.is_colliding]
    for _ in range(MAX_COLLISION_ITERATIONS): # Loop a few times to resolve stacked collisions
        max_depth = -1.0
        best_collision = None # (collided_object, normal, depth)
        collision_found_this_iteration = False

        for obj in collidable_objects:
            # Broad phase (AABB check)
            if isinstance(obj, Terrain):
                obj_rect = obj.rect
            elif isinstance(obj, Obstacle):
                 obj_rect = obj.get_rotated_rect()
            else:
                 continue

            if not ball.rect.colliderect(obj_rect):
                continue

            # Narrow phase
            if isinstance(obj, Terrain):
                poly_points = obj.points
            else: # Obstacle
                poly_points = [(p + obj.position) for p in obj.rotated_points]
                if not poly_points: continue

            normal, depth = pygame.Vector2(0,0), 0
            try:
                normal, depth = get_polygon_collision_normal_depth(
                    poly_points, ball.position, ball.scaled_radius
                )
            except Exception as e:
                 print(f"Error during collision check with {type(obj)}: {e}")
                 continue

            if normal and depth > 1e-4: # Found a penetration
                collision_found_this_iteration = True
                # Track the collision with the maximum depth in this iteration
                if depth > max_depth:
                    max_depth = depth
                    best_collision = (obj, normal, depth)

        # --- Process the deepest collision found in this iteration ---
        if best_collision:
            collided_object, normal, depth = best_collision

            # 3a. Resolve Penetration
            # Push slightly more than depth to ensure clearance
            push_distance = depth * COLLISION_PUSH_FACTOR
            ball.position += normal * push_distance
            ball.rect.center = ball.position

            # 3b. Calculate Collision Response (Bounce and Friction)
            bounce = getattr(collided_object, 'bounce_factor', 0.4)
            friction = getattr(collided_object, 'friction', 0.3)

            vn_scalar = ball.velocity.dot(normal)
            normal_velocity = vn_scalar * normal
            tangent_velocity = ball.velocity - normal_velocity

            if vn_scalar < 0: # Moving into the surface
                new_vn_scalar = -vn_scalar * bounce
                if abs(new_vn_scalar) < MIN_BOUNCE_VELOCITY and abs(vn_scalar) > MIN_BOUNCE_VELOCITY / 2:
                     new_vn_scalar = MIN_BOUNCE_VELOCITY
                normal_velocity = new_vn_scalar * normal
            else: # Moving away or parallel
                 normal_velocity *= bounce # Still apply bounce factor

            tangent_speed = tangent_velocity.length()
            if tangent_speed > 1e-5:
                # Assuming friction is a coefficient (0=no friction, 1=full stop)
                # new_vt = vt * (1.0 - friction_coefficient)
                friction_effect = max(0, 1.0 - friction)
                tangent_velocity *= friction_effect

            ball.velocity = normal_velocity + tangent_velocity

            # 3c. Handle Collision Toggling (Anti-Stuck) - Check only after resolving
            ball.update_collision_state(collided_object)
            if ball.is_stuck():
                ball.velocity = pygame.Vector2(0, 0)
                ball.is_moving = False
                ball.reset_collision_state()
                print("Ball stuck, stopping.")
                return False # Exit physics update immediately if stuck

        # If no collisions were found in this iteration, exit the resolution loop
        if not collision_found_this_iteration:
            break
    # --- End of Iterative Collision Resolution Loop ---

    # Reset anti-stuck state if the ball wasn't stuck and ended the loop without collision
    if best_collision is None: # No collision in the last iteration
         ball.reset_collision_state()


    # 4. Check for Stopping Condition (after all resolutions for this sub-step)
    if ball.velocity.length_squared() < STOP_SPEED_THRESHOLD**2:
        # Check if reasonably flat only if there was a collision resolved in the last iteration
        is_on_flat_surface = False
        if best_collision: # Check the normal from the last resolved collision
            _, normal, _ = best_collision
            if abs(normal.y) > 0.9: # Check if mostly vertical normal
                is_on_flat_surface = True

        # Stop if slow enough AND (no collision resolved OR on a flat surface)
        if best_collision is None or is_on_flat_surface:
            ball.velocity = pygame.Vector2(0, 0)
            ball.is_moving = False
            ball.reset_collision_state()
            return False

    # If we reach here, the ball is still considered moving after this sub-step
    return True
