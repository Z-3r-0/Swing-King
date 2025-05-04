import math
import pygame # Import pygame for Vector2

# --- Collision Helper Functions ---

# project_polygon and project_circle are no longer needed by the optimized
# get_polygon_collision_normal_depth, but might be useful elsewhere.
# Keep them for now, or remove if definitely unused.
def project_polygon(axis, points):
    """Projects a polygon onto an axis."""
    min_proj = float('inf')
    max_proj = float('-inf')
    for point in points:
        projection = axis.dot(point)
        min_proj = min(min_proj, projection)
        max_proj = max(max_proj, projection)
    return min_proj, max_proj

def project_circle(axis, center, radius):
    """Projects a circle onto an axis."""
    projection = axis.dot(center)
    min_proj = projection - radius
    max_proj = projection + radius
    return min_proj, max_proj

def get_polygon_collision_normal_depth(poly_points, ball_center, ball_radius):
    """
    Optimized: Calculates collision normal and depth by finding the closest
    point on the polygon to the ball center. Assumes broad-phase (AABB)
    check has already passed.

    Args:
        poly_points: List of Vector2 points defining the polygon (world coords).
        ball_center: Vector2 position of the ball's center (world coords).
        ball_radius: Float radius of the ball.

    Returns:
        (normal, depth) or (None, 0). Normal points away from the polygon
        towards the ball. Depth is the penetration amount.
    """
    points = poly_points
    num_points = len(points)

    if num_points < 2: # Need at least a line segment
        return None, 0

    closest_point_on_poly = None
    min_dist_sq = float('inf')

    # --- Find Closest Point on Polygon Boundary ---
    for i in range(num_points):
        p1 = points[i]
        p2 = points[(i + 1) % num_points] # Next vertex with wrap-around
        edge = p2 - p1
        edge_len_sq = edge.length_squared()

        # Vector from segment start (p1) to ball center
        segment_to_ball = ball_center - p1

        # Calculate projection parameter 't' of ball center onto the infinite line
        # Clamp 't' to [0, 1] to find the closest point on the *segment*
        if edge_len_sq > 1e-9: # Avoid division by zero for zero-length edges
            t = segment_to_ball.dot(edge) / edge_len_sq
            t = max(0.0, min(1.0, t)) # Clamp to segment
        else:
            t = 0.0 # If edge is a point, closest point is p1

        # Calculate the closest point on this specific segment
        point_on_segment = p1 + t * edge

        # Calculate squared distance from ball center to this point on segment
        dist_sq = ball_center.distance_squared_to(point_on_segment)

        # Update overall closest point if this one is closer
        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            closest_point_on_poly = point_on_segment

    # --- Check for Collision and Calculate Response ---
    # If a closest point was found and it's within the ball's radius (allowing for small float errors)
    if closest_point_on_poly is not None and min_dist_sq < (ball_radius * ball_radius) + 1e-5:
        dist = math.sqrt(min_dist_sq)
        depth = ball_radius - dist

        # Ensure depth is meaningfully positive before reporting collision
        if depth > 1e-5:
            # Calculate normal pointing from closest point towards ball center
            if dist > 1e-6: # Avoid normalization if ball center is (almost) exactly on the point
                normal = (ball_center - closest_point_on_poly).normalize()
            else:
                # Ball center is extremely close or on the boundary.
                # We need *some* normal. A fallback pointing straight up might suffice,
                # or ideally, we could try getting the normal of the segment it's on.
                # Let's try segment normal as a fallback:
                # Find the segment that yielded the closest point (requires storing 'i' or the segment)
                # For simplicity now, use an arbitrary fallback.
                # print("Warning: Ball center very close to polygon boundary. Using fallback normal.")
                normal = pygame.Vector2(0, -1) # Arbitrary up normal (adjust if needed)
                # A better fallback might involve checking the segment normal if dist is near zero.

            return normal, depth # Return the calculated normal and depth
        else:
            # Depth is negligible, treat as no collision
            return None, 0
    else:
        # Closest point is outside the ball's radius, no collision
        return None, 0


# --- Trajectory Prediction ---
# (This function remains unchanged)
def draw_predicted_trajectory(
    surface: pygame.Surface,
    start_pos: pygame.Vector2,
    initial_velocity: pygame.Vector2,
    gravity: float,
    damping: float,
    dt: float,
    steps: int,
    camera_offset: pygame.Vector2,
    color: tuple,
    radius: int,
    spacing: int
):
    """
    Draws a predicted trajectory using simple Euler integration with damping.

    Args:
        surface: Pygame surface to draw on.
        start_pos: Initial world position (Vector2) of the ball.
        initial_velocity: Initial world velocity (Vector2) of the ball.
        gravity: Gravitational acceleration (positive value, pixels/s^2).
        damping: Damping factor applied each frame (e.g., 0.99).
        dt: Time step for simulation (seconds).
        steps: Number of simulation steps to predict.
        camera_offset: Camera's world position (Vector2) to convert world to screen.
        color: Color of the trajectory dots.
        radius: Radius of the trajectory dots.
        spacing: Draw a dot every 'spacing' steps.
    """
    if initial_velocity.length_squared() == 0:
        return

    position = start_pos.copy()
    velocity = initial_velocity.copy()
    steps_since_last_dot = 0

    for i in range(steps):
        # Update velocity (gravity and damping)
        velocity.y += gravity * dt
        velocity *= damping

        # Update position
        position += velocity * dt

        # Draw dot periodically
        steps_since_last_dot += 1
        if steps_since_last_dot >= spacing:
            screen_pos = position - camera_offset
            # Basic screen bounds check
            if 0 <= screen_pos.x <= surface.get_width() and 0 <= screen_pos.y <= surface.get_height():
                 pygame.draw.circle(surface, color, screen_pos, radius)
            steps_since_last_dot = 0

        # Optional: Stop prediction if velocity is very low
        if velocity.length_squared() < 1.0:
            break