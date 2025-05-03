import math
import pygame # Import pygame for Vector2

# --- Collision Helper Functions ---

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
    Calculates the collision normal and penetration depth for a ball colliding
    with a convex polygon using Separating Axis Theorem ideas combined with
    closest point calculation for better normal/depth accuracy.

    Assumes poly_points are Vector2 in world coordinates.
    Returns (normal, depth) or (None, 0). Normal points away from the polygon towards the ball.
    """
    min_depth = float('inf')
    collision_normal = None
    axis_normal = None # Store the potential normal from SAT edge check

    points = poly_points # Assume they are already Vector2
    num_points = len(points)

    if num_points < 2: # Need at least a line segment
        return None, 0

    # --- SAT Check (Primarily for early exit) ---
    # 1. Check Polygon Edges
    for i in range(num_points):
        p1 = points[i]
        p2 = points[(i + 1) % num_points]
        edge = p2 - p1
        if edge.length_squared() < 1e-9: continue # Skip zero-length edges

        # Normal perpendicular to the edge
        edge_normal = pygame.Vector2(-edge.y, edge.x)
        if edge_normal.length_squared() < 1e-9: continue
        edge_normal = edge_normal.normalize()

        min_proj_poly, max_proj_poly = project_polygon(edge_normal, points)
        min_proj_ball, max_proj_ball = project_circle(edge_normal, ball_center, ball_radius)

        # Check for separation
        if max_proj_ball < min_proj_poly - 1e-5 or max_proj_poly < min_proj_ball - 1e-5:
            return None, 0 # Separating axis found

        # Calculate overlap on this axis
        overlap = min(max_proj_poly, max_proj_ball) - max(min_proj_poly, min_proj_ball)

        # Store the axis normal corresponding to the minimum overlap found so far
        if overlap < min_depth:
            min_depth = overlap
            axis_normal = edge_normal # Potential collision normal

    # 2. Check Axes from Ball Center to Polygon Vertices (Needed for circle-vertex collision)
    for vertex in points:
        axis = (ball_center - vertex)
        if axis.length_squared() < 1e-9: continue # Skip if ball center is on vertex
        axis = axis.normalize()

        min_proj_poly, max_proj_poly = project_polygon(axis, points)
        min_proj_ball, max_proj_ball = project_circle(axis, ball_center, ball_radius)

        # Check for separation
        if max_proj_ball < min_proj_poly - 1e-5 or max_proj_poly < min_proj_ball - 1e-5:
            return None, 0 # Separating axis found

    # --- Closest Point Check (For accurate normal and depth) ---
    # If SAT didn't find separation, a collision is likely. Find the closest point.
    closest_point_on_poly = None
    min_dist_sq = float('inf')

    for i in range(num_points):
        p1 = points[i]
        p2 = points[(i + 1) % num_points]
        edge = p2 - p1
        segment_vec = ball_center - p1
        edge_len_sq = edge.length_squared()

        if edge_len_sq > 1e-9: # Avoid division by zero for zero-length edges
            t = segment_vec.dot(edge) / edge_len_sq
            t = max(0.0, min(1.0, t)) # Clamp to segment
        else:
            t = 0.0 # Treat as point p1 if edge has no length

        point_on_segment = p1 + t * edge
        dist_sq = ball_center.distance_squared_to(point_on_segment)

        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            closest_point_on_poly = point_on_segment

    # If a closest point was found and it's within the ball's radius
    if closest_point_on_poly is not None and min_dist_sq < (ball_radius * ball_radius) + 1e-5:
        dist = math.sqrt(min_dist_sq)
        depth = ball_radius - dist

        # Ensure depth is positive before reporting collision
        if depth > 1e-5:
            # Calculate normal pointing from closest point towards ball center
            if dist > 1e-6:
                normal = (ball_center - closest_point_on_poly).normalize()
            else:
                # Ball center is very close/on boundary. Use the SAT axis normal.
                # Ensure it points towards the ball.
                if axis_normal is not None:
                    if axis_normal.dot(ball_center - closest_point_on_poly) < 0:
                         normal = -axis_normal # Flip if pointing wrong way
                    else:
                         normal = axis_normal
                else:
                    # Fallback: If SAT somehow failed but closest point check passed
                    # This case is unlikely if SAT is correct. Use an arbitrary normal.
                    print("Warning: Closest point collision detected but no SAT axis found.")
                    normal = pygame.Vector2(0, -1) # Arbitrary up normal

            return normal, depth # Return normal from closest point and calculated depth

    # If closest point is outside radius or no closest point found (shouldn't happen if SAT passed)
    return None, 0


# --- Trajectory Prediction ---

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