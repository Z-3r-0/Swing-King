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



def distance_point_to_segment_vector(point_p: pygame.Vector2, seg_a: pygame.Vector2, seg_b: pygame.Vector2) -> float:
    """
    Return the distance from point_p to the line segment defined by seg_a and seg_b, using pygame.Vector2.
    """
    # Vector representing the line segment
    segment_vec = seg_b - seg_a
    # Vector from the segment start to the point
    point_vec = point_p - seg_a

    segment_len_sq = segment_vec.magnitude_squared()

    # If the segment is essentially a point
    if segment_len_sq < 1e-10: # Use a small epsilon for float comparison
        return point_vec.length()

    # Calculate the projection factor 't' of the point onto the infinite line
    # t = dot_product(AP, AB) / length_squared(AB)
    t = point_vec.dot(segment_vec) / segment_len_sq

    # Clamp t to the range [0, 1] to restrict to the segment
    t = max(0.0, min(1.0, t))

    # Calculate the closest point on the segment
    closest_point_on_segment = seg_a + t * segment_vec

    # Return the distance between the original point and the closest point on the segment
    return point_p.distance_to(closest_point_on_segment)


def get_collision_edge_angle_vector(polygon_points, collision_point):
    """
    Given a list of polygon points (tuples) and a collision point (tuple),
    determine the angle (in degrees) of the polygon edge closest to the collision point.
    Uses pygame.Vector2 internally.

    Returns a tuple (angle_degrees, edge_tuples) where edge_tuples is ((x1, y1), (x2, y2)).
    """
    if not collision_point:
        return None, None

    # Convert inputs to vectors
    collision_vec = pygame.Vector2(collision_point)
    polygon_vecs = [pygame.Vector2(p) for p in polygon_points]

    min_dist = float('inf')
    best_edge_vecs = None # Store the best edge as vectors
    num_points = len(polygon_vecs)

    # Loop through each edge of the polygon using vectors
    for i in range(num_points):
        pt1_vec = polygon_vecs[i]
        pt2_vec = polygon_vecs[(i + 1) % num_points] # wrap-around for last segment

        # Use the vectorized distance function
        dist = distance_point_to_segment_vector(collision_vec, pt1_vec, pt2_vec)

        if dist < min_dist:
            min_dist = dist
            best_edge_vecs = (pt1_vec, pt2_vec)

    if best_edge_vecs is None:
        return None, None

    # Compute the angle of the best edge relative to the horizontal axis
    edge_vector = best_edge_vecs[1] - best_edge_vecs[0]

    # Handle zero-length edge vector case (shouldn't happen with valid polygons)
    if edge_vector.length_squared() < 1e-10:
         angle_deg = 0.0 # Or handle as an error/None
    else:
        # angle_to gives angle relative to the positive x-axis in degrees [-180, 180]
        angle_deg = pygame.Vector2(1, 0).angle_to(edge_vector)
        # Optional: Normalize to [0, 360) if preferred
        # angle_deg = (angle_deg + 360) % 360

    # Convert the best edge vectors back to tuples for the return value,
    # maintaining the original expected output format.
    best_edge_tuples = (best_edge_vecs[0].xy, best_edge_vecs[1].xy)

    return angle_deg, best_edge_tuples

def get_closest_edge_normal(polygon_points, collision_point_global):
    """
    Retourne la normale du segment du polygone le plus proche du point de collision.
    :param polygon_points: liste des points du polygone [(x1,y1), (x2,y2), ...]
    :param collision_point_global: point d'impact (x, y)
    :return: normale (pygame.Vector2)
    """
    closest_distance = float('inf')
    closest_normal = None

    for i in range(len(polygon_points)):
        p1 = pygame.Vector2(polygon_points[i])
        p2 = pygame.Vector2(polygon_points[(i + 1) % len(polygon_points)])
        # Projection du point sur le segment
        edge = p2 - p1
        edge_length_squared = edge.length_squared()
        if edge_length_squared == 0:
            continue

        t = max(0, min(1, (pygame.Vector2(collision_point_global) - p1).dot(edge) / edge_length_squared))
        projection = p1 + t * edge
        dist = (pygame.Vector2(collision_point_global) - projection).length()

        if dist < closest_distance:
            closest_distance = dist
            normal = edge.rotate(90).normalize()  # Perpendiculaire
            closest_normal = normal

    return closest_normal

def get_collision_normal_and_depth(polygon_points, collision_point, ball_center, ball_pixel_radius):
    """
    :param polygon_points: liste de (x,y) en pixels du polygone
    :param collision_point: point d'impact issu de mask.overlap(), en pixels globaux
    :param ball_center: pygame.Vector2 du centre de la balle en pixels
    :param ball_pixel_radius: rayon de la balle en pixels (radius * scale_value)
    :return: (normal: Vector2 unitaire pointant vers l'extérieur, depth: float en pixels)
    """
    # 1) Trouver l'arête la plus proche
    closest_dist = float('inf')
    best_edge = None
    best_proj = None

    for i in range(len(polygon_points)):
        p1 = pygame.Vector2(polygon_points[i])
        p2 = pygame.Vector2(polygon_points[(i+1) % len(polygon_points)])
        edge = p2 - p1
        seg_len2 = edge.length_squared()
        if seg_len2 == 0:
            continue

        # projection du centre de la balle sur l'arête
        t = (ball_center - p1).dot(edge) / seg_len2
        t = max(0.0, min(1.0, t))
        proj = p1 + t * edge

        dist = (ball_center - proj).length()
        if dist < closest_dist:
            closest_dist = dist
            best_edge = edge
            best_proj = proj

    if best_edge is None:
        return None, 0

    # 2) calcul de la normale perpendiculaire
    # on prend (-dy, dx) pour avoir un perpendicular
    normal = pygame.Vector2(-best_edge.y, best_edge.x)
    normal_len = normal.length()
    if normal_len == 0:
        return None, 0
    normal = normal / normal_len

    # 3) orientation : on veut que normal pointe vers la balle
    if normal.dot(ball_center - best_proj) < 0:
        normal = -normal

    # 4) profondeur de pénétration
    depth = ball_pixel_radius - closest_dist

    return normal, depth



# --- Helper Function: Polygon-Circle Collision ---
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

    # Find the closest point on the polygon's boundary to the ball's center
    for i in range(len(poly_points_world)):
        p1 = poly_points_world[i]
        p2 = poly_points_world[(i + 1) % len(poly_points_world)]  # Next vertex with wrap-around
        edge = p2 - p1
        edge_len_sq = edge.length_squared()

        segment_to_ball_center = ball_center_world - p1

        t = 0.0
        if edge_len_sq > 1e-9:  # Avoid division by zero for zero-length edges
            t = segment_to_ball_center.dot(edge) / edge_len_sq
            t = max(0.0, min(1.0, t))  # Clamp t to [0, 1] for segment

        point_on_segment = p1 + t * edge
        dist_sq_to_segment_point = ball_center_world.distance_squared_to(point_on_segment)

        if dist_sq_to_segment_point < min_dist_sq:
            min_dist_sq = dist_sq_to_segment_point
            closest_point_on_poly = point_on_segment

    if closest_point_on_poly is None:  # Should not happen if poly_points is valid
        return None, 0

    # Check for collision: if distance to closest point is less than ball's radius
    if min_dist_sq < (ball_radius * ball_radius) + 1e-5:  # Add epsilon for float precision
        dist = math.sqrt(min_dist_sq)
        depth = ball_radius - dist

        if depth > 1e-5:  # Ensure meaningful penetration
            normal = pygame.Vector2(0, -1)  # Default normal (e.g., up)
            if dist > 1e-6:  # Avoid normalization of zero vector
                normal = (ball_center_world - closest_point_on_poly).normalize()
            # else: ball center is (almost) on the polygon edge/vertex.
            # A more robust normal might be found from the edge itself, but this is often sufficient.
            return normal, depth
        else:
            return None, 0  # Negligible depth
    else:
        return None, 0  # No collision


# --- Core Physics Update Function ---
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

    # 1. Apply Forces (Gravity and Damping)
    ball.velocity.y += GRAVITY_ACCELERATION * dt
    # Frame-rate independent damping approximation
    # (damping factor applied per second would be DEFAULT_DAMPING_FACTOR)
    # Effective damping for this dt:
    effective_damping = DEFAULT_DAMPING_FACTOR ** dt
    ball.velocity *= effective_damping

    # 2. Update Position based on current velocity
    ball.position += ball.velocity * dt
    ball.rect.center = ball.position  # Keep ball's Pygame Rect updated

    # 3. Iterative Collision Detection and Resolution Loop
    # Obstacles are already filtered for is_colliding in the Game class before passing here.
    collidable_entities = terrain_polys + obstacles

    collision_resolved_this_sub_step = False

    for _ in range(MAX_PHYSICS_COLLISION_ITERATIONS):
        max_penetration_depth = -1.0
        most_significant_collision = None  # Stores (collided_object, normal, depth)
        found_collision_this_iteration = False

        for entity in collidable_entities:
            # Broad phase: AABB (Axis-Aligned Bounding Box) check
            entity_rect = entity.rect

            ball_scaled_radius = ball.radius * ball.scale_value
            if not ball.rect.colliderect(entity_rect):
                continue

            # Narrow phase: More precise collision check
            entity_world_points = []
            if isinstance(entity, Terrain):
                entity_world_points = [pygame.Vector2(p) for p in entity.points]
            elif isinstance(entity, Obstacle):
                # Obstacle points are relative to its top-left; convert to world coordinates
                entity_world_points = [(pygame.Vector2(p) + entity.position) for p in entity.rotated_points]

            if not entity_world_points or len(entity_world_points) < 2:
                continue  # Not enough points to form a collidable shape

            normal, depth = get_polygon_collision_normal_depth(
                entity_world_points, ball.position, ball_scaled_radius
            )

            if normal and depth > 1e-4:  # If a collision with penetration is found
                found_collision_this_iteration = True
                if depth > max_penetration_depth:
                    max_penetration_depth = depth
                    most_significant_collision = (entity, normal, depth)

        # --- Process the most significant collision found in this iteration ---
        if most_significant_collision:
            collided_object, normal_vec, penetration_depth = most_significant_collision
            collision_resolved_this_sub_step = True  # Mark that a collision was handled

            # Anti-stuck mechanism (using game_instance for state)
            current_object_id = id(collided_object)
            if game_instance.physics_last_collided_object_id is not None and \
                    current_object_id != game_instance.physics_last_collided_object_id:
                game_instance.physics_collision_toggle_count += 1
            else:  # Colliding with the same object again or first collision in this sequence
                game_instance.physics_collision_toggle_count = 0
            game_instance.physics_last_collided_object_id = current_object_id

            if game_instance.physics_collision_toggle_count >= game_instance.max_toggle_toggles:
                ball.velocity = pygame.Vector2(0, 0)
                ball.is_moving = False
                # Reset anti-stuck state for the next shot/movement
                game_instance.physics_last_collided_object_id = None
                game_instance.physics_collision_toggle_count = 0
                return False  # Ball is stuck, stop physics update

            # 3a. Resolve Penetration: Push ball out of the collision
            ball.position += normal_vec * (penetration_depth * COLLISION_PENETRATION_PUSH_FACTOR)
            ball.rect.center = ball.position

            # 3b. Calculate Collision Response (Bounce and Friction)
            bounce_coeff = getattr(collided_object, 'bounce_factor', 0.4)  # Default bounce
            friction_coeff = getattr(collided_object, 'friction',0.3)  # Default friction (0 to 1, where 0.3 means 30% energy loss)

            if friction_coeff < 0:  # If we touched a restart zone
                # print("Touched water or dead zone")
                pygame.event.post(pygame.event.Event(pygame.USEREVENT + 30))  # (see events.py file)

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
            # else: Ball is moving away or parallel, normal velocity component is already correct or will be damped

            # Apply friction to tangent velocity: new_vt = vt * (1.0 - friction_coefficient)
            tangent_velocity_vector *= (1.0 - friction_coeff)
            ball.velocity = normal_velocity_vector + tangent_velocity_vector

        if not found_collision_this_iteration:
            # If no collisions were found in this iteration, the ball is clear (for now)
            break  # Exit the iterative collision resolution loop
    # --- End of Iterative Collision Resolution Loop for this sub-step ---

    # If the ball went through all iterations without any collision being resolved,
    # it means it's flying free or sliding without new penetrations.
    # Reset part of the anti-stuck if it wasn't stuck and ended loop without collision.
    if not collision_resolved_this_sub_step:
        game_instance.physics_last_collided_object_id = None
        # game_instance.physics_collision_toggle_count = 0 # Keep count unless ball fully stops or new shot

    # 4. Check for Stopping Condition (after all resolutions for this sub-step)
    if ball.velocity.length_squared() < BALL_STOP_SPEED_THRESHOLD ** 2:
        is_on_flat_surface = False
        if collision_resolved_this_sub_step and most_significant_collision:
            # Check the normal from the last resolved collision in this sub-step
            _, last_normal, _ = most_significant_collision
            if abs(last_normal.y) > 0.9:  # Check if normal is mostly vertical (flat ground)
                is_on_flat_surface = True

        # Stop if slow enough AND (no collision was resolved OR it stopped on a flat surface)
        if not collision_resolved_this_sub_step or is_on_flat_surface:
            ball.velocity = pygame.Vector2(0, 0)
            ball.is_moving = False
            # Fully reset anti-stuck state when ball stops
            game_instance.physics_last_collided_object_id = None
            game_instance.physics_collision_toggle_count = 0
            return False  # Ball has stopped

    # If we reach here, the ball is still considered moving after this sub-step
    return True