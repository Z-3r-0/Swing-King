import os
import random

import pygame
import math
from src.entities import Obstacle, Terrain

# --- Constants ---
GRAVITY_ACCELERATION = 980.0  # Gravitational acceleration in pixels/s²
DEFAULT_DAMPING_FACTOR = 0.90  # Velocity multiplier per frame to simulate air/rolling resistance
BALL_STOP_SPEED_THRESHOLD = 8.0  # Speed (pixels/s) below which the ball is considered stopped
MIN_BOUNCE_VELOCITY_NORMAL = 15.0  # Minimum velocity component normal to surface after bounce
COLLISION_PENETRATION_PUSH_FACTOR = 1.01  # Factor to push ball out of penetration (slightly > 1)
MAX_PHYSICS_COLLISION_ITERATIONS = 3  # Max times to re-check collisions within one sub-step

pygame.mixer.init()
grass_sound = pygame.mixer.Sound("assets/audio/sound_effect/rebounds/rebond_herbe.mp3")
rock_sound_1 = pygame.mixer.Sound("assets/audio/sound_effect/rebounds/rebond_pierre.mp3")
rock_sound_2 = pygame.mixer.Sound("assets/audio/sound_effect/rebounds/rebond_pierre2.mp3")

rock_sounds = [rock_sound_1, rock_sound_2]

defeat_effects = []
for effect in os.listdir("assets/audio/sound_effect/defeat"):
    sound = pygame.mixer.Sound("assets/audio/sound_effect/defeat/" + effect)
    defeat_effects.append(sound)

water_effects = []
for effect in os.listdir("assets/audio/sound_effect/water"):
    sound = pygame.mixer.Sound("assets/audio/sound_effect/water/" + effect)
    water_effects.append(sound)
    
sand_effect = pygame.mixer.Sound("assets/audio/sound_effect/rebounds/rebond_sable.mp3")


played_sound = False

def get_polygon_collision_normal_depth(poly_points_world, ball_center_world, ball_radius):
    """
    Calculates collision normal and depth for a circle and a convex polygon.
    Normal points away from the polygon towards the ball. Depth is penetration.

    Args:
        poly_points_world: List of pygame.Vector2 points defining the polygon in world coordinates.
        ball_center_world: pygame.Vector2 position of the ball's center in world coordinates.
        ball_radius: Float radius of the ball.

    Returns:
        (normal_vector, depth_value) or (None, 0) if no collision.
    """
    if not poly_points_world or len(poly_points_world) < 2:
        return None, 0

    closest_point_on_poly = None
    min_dist_sq = float('inf')

    # Find the closest point
    for i in range(len(poly_points_world)):
        p1 = poly_points_world[i]
        p2 = poly_points_world[(i + 1) % len(poly_points_world)]  # Wrap around to the first point
        edge = p2 - p1
        edge_len_sq = edge.length_squared()

        segment_to_ball_center = ball_center_world - p1

        t = 0.0
        if edge_len_sq > 1e-9:  # non-zero edge length
            t = segment_to_ball_center.dot(edge) / edge_len_sq
            t = max(0.0, min(1.0, t))  # Clamp t to [0, 1] for segment

        point_on_segment = p1 + t * edge
        dist_sq_to_segment_point = ball_center_world.distance_squared_to(point_on_segment)

        if dist_sq_to_segment_point < min_dist_sq:
            min_dist_sq = dist_sq_to_segment_point
            closest_point_on_poly = point_on_segment

    if closest_point_on_poly is None: # No valid closest point found
        return None, 0

    # Check for collision: if distance to closest point is less than ball's radius
    if min_dist_sq < (ball_radius * ball_radius) + 1e-5:  # Add epsilon for float precision
        dist = math.sqrt(min_dist_sq)
        depth = ball_radius - dist

        if depth > 1e-5: # Avoid zero or negative depth
            normal = pygame.Vector2(0, -1) # Default normal
            if dist > 1e-6:  # Avoid normalization of zero vector
                normal = (ball_center_world - closest_point_on_poly).normalize()
            return normal, depth
        else:
            return None, 0  # No penetration
    else:
        return None, 0  # No collision


def update_ball_physics(ball, terrain_polys, obstacles, dt, game_instance):
    """
    Updates the ball's position, velocity, and handles collisions for one fixed sub-step (dt).

    Args:
        ball: The Ball object.
        terrain_polys: List of Terrain objects.
        obstacles: List of collidable Obstacle objects.
        dt: Fixed time delta for the sub-step (in seconds).
        game_instance: The Game class instance, for accessing/modifying game-level state
                       like anti-stuck counters (`physics_last_collided_object_id`,
                       `physics_collision_toggle_count`, `max_toggle_toggles`).

    Returns:
        bool: True if the ball is still considered moving after this sub-step, False otherwise.
    """
    if not ball.is_moving:
        return False
    
    global played_sound

    # apply gravity to the ball's velocity
    ball.velocity.y += GRAVITY_ACCELERATION * dt
    # Apply damping to the ball's velocity
    effective_damping = DEFAULT_DAMPING_FACTOR ** dt
    ball.velocity *= effective_damping

    # Update Ball Position
    ball.position += ball.velocity * dt
    ball.rect.center = ball.position  # keep ball Rect updated

    # collision detection and resolution
    collidable_entities = terrain_polys + obstacles

    collision_resolved_this_sub_step = False

    for _ in range(MAX_PHYSICS_COLLISION_ITERATIONS):
        max_penetration_depth = -1.0
        most_significant_collision = None  # keep (collided_object, normal, depth)
        found_collision_this_iteration = False

        for entity in collidable_entities:
            # bounding box check
            entity_rect = entity.rect

            ball_scaled_radius = ball.radius * ball.scale_value
            if not ball.rect.colliderect(entity_rect):
                continue

            # more precise collision check with mask
            entity_world_points = []
            if isinstance(entity, Terrain):
                entity_world_points = [pygame.Vector2(p) for p in entity.points]
                
            elif isinstance(entity, Obstacle):
                # Obstacle points are relative to topleft, convert to world coordinate
                entity_world_points = [(pygame.Vector2(p) + entity.position) for p in entity.rotated_points]

            if not entity_world_points or len(entity_world_points) < 2:
                continue  # Not enough points

            normal, depth = get_polygon_collision_normal_depth(entity_world_points, ball.position, ball_scaled_radius)

            if normal and depth > 1e-4:  # If a collision with penetration is found
                found_collision_this_iteration = True
                if depth > max_penetration_depth:
                    max_penetration_depth = depth
                    most_significant_collision = (entity, normal, depth)

        # Find best collision
        if most_significant_collision:
            collided_object, normal_vec, penetration_depth = most_significant_collision
            collision_resolved_this_sub_step = True  # Mark that a collision was handled

            # Anti-stuck mechanism
            current_object_id = id(collided_object)
            if game_instance.physics_last_collided_object_id is not None and \
                    current_object_id != game_instance.physics_last_collided_object_id:
                game_instance.physics_collision_toggle_count += 1
            else:  # Colliding with the same object again
                game_instance.physics_collision_toggle_count = 0
            game_instance.physics_last_collided_object_id = current_object_id

            if game_instance.physics_collision_toggle_count >= game_instance.max_toggle_toggles:
                ball.velocity = pygame.Vector2(0, 0)
                ball.is_moving = False
                # Reset anti-stuck state for the next shot
                game_instance.physics_last_collided_object_id = None
                game_instance.physics_collision_toggle_count = 0
                return False  # Ball is stuck, stop physics update

            # Push ball out of the collision to escape penetration
            ball.position += normal_vec * (penetration_depth * COLLISION_PENETRATION_PUSH_FACTOR)
            ball.rect.center = ball.position

            # compute new velocity
            bounce_coeff = getattr(collided_object, 'bounce_factor', 0.4)
            friction_coeff = getattr(collided_object, 'friction',0.3)

            terrain_type = getattr(collided_object, 'terrain_type', Terrain)

            if terrain_type == "green" or terrain_type == "fairway" or terrain_type == "darkgreen":
                grass_sound.play()
            elif terrain_type == "rocks" or terrain_type == "darkrocks":
                random.choice(rock_sounds).play()
            elif terrain_type == "bunker":
                sand_effect.play()

            velocity_normal_component_scalar = ball.velocity.dot(normal_vec)
            normal_velocity_vector = velocity_normal_component_scalar * normal_vec
            tangent_velocity_vector = ball.velocity - normal_velocity_vector

            if velocity_normal_component_scalar < 0:  # Ball is moving into the surface
                new_normal_scalar = -velocity_normal_component_scalar * bounce_coeff
                # Ensure minimum bounce velocity if it was significant before impact
                if abs(new_normal_scalar) < MIN_BOUNCE_VELOCITY_NORMAL and \
                        abs(velocity_normal_component_scalar) > MIN_BOUNCE_VELOCITY_NORMAL / 2:
                    # Preserve sign for bounce direction
                    new_normal_scalar = MIN_BOUNCE_VELOCITY_NORMAL if new_normal_scalar >= 0 else -MIN_BOUNCE_VELOCITY_NORMAL
                normal_velocity_vector = new_normal_scalar * normal_vec

            # Apply friction to tangent velocity
            tangent_velocity_vector *= (1.0 - friction_coeff)
            ball.velocity = normal_velocity_vector + tangent_velocity_vector

            if friction_coeff < 0:

                pygame.event.post(pygame.event.Event(pygame.USEREVENT + 30))

                if not played_sound:
                    if getattr(collided_object, 'terrain_type') == "lake":
                        random.choice(water_effects).play()
                        played_sound = True
                    else:
                        random.choice(defeat_effects).play()
                        played_sound = True

                break

        if not found_collision_this_iteration:
            # If no collisions were found in this iteration, the ball is clear
            played_sound = False
            break

    # Ball is still moving, but check if it is on a flat surface
    if not collision_resolved_this_sub_step:
        game_instance.physics_last_collided_object_id = None


    # Check for Stopping Condition
    if ball.velocity.length_squared() < BALL_STOP_SPEED_THRESHOLD ** 2:
        is_on_flat_surface = False
        if collision_resolved_this_sub_step and most_significant_collision:
            # Check the normal from the last resolved collision in this sub-step
            _, last_normal, _ = most_significant_collision
            if abs(last_normal.y) > 0.9:  # Check if flat ground
                is_on_flat_surface = True

        # Stop if slow enough
        if not collision_resolved_this_sub_step or is_on_flat_surface:
            ball.velocity = pygame.Vector2(0, 0)
            ball.is_moving = False
            # Fully reset anti-stuck state when ball stops
            game_instance.physics_last_collided_object_id = None
            game_instance.physics_collision_toggle_count = 0
            return False  # Ball has stopped
        
    return True